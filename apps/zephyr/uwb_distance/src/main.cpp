/*
 * Copyright (c) 2015-2016 Wind River Systems, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @file C++ Synchronization demo.  Uses basic C++ functionality.
 */

#include <stdio.h>
#include <zephyr.h>
#include <arch/cpu.h>
#include <sys/printk.h>

#include <device.h>
#include <devicetree.h>
#include <drivers/gpio.h>
#include <drivers/spi.h>
/**
 * @class semaphore the basic pure virtual semaphore class
 */
class semaphore {
public:
	virtual int wait(void) = 0;
	virtual int wait(int timeout) = 0;
	virtual void give(void) = 0;
};

/* specify delay between greetings (in ms); compute equivalent in ticks */
#define SLEEPTIME 5500
#define STACKSIZE 2000

#define LED_TX_NODE DT_ALIAS(led0)
#define LED_RX_NODE DT_ALIAS(led1)
#define GPIO_RSTN_NODE DT_ALIAS(led2)

#if DT_NODE_HAS_STATUS(LED_TX_NODE, okay)
#define LED_TX_LABEL	DT_GPIO_LABEL(LED_TX_NODE, gpios)
#define LED_TX_PIN	DT_GPIO_PIN(LED_TX_NODE, gpios)
#define LED_TX_FLAGS	DT_GPIO_FLAGS(LED_TX_NODE, gpios)
#endif

#if DT_NODE_HAS_STATUS(LED_RX_NODE, okay)
#define LED_RX_LABEL	DT_GPIO_LABEL(LED_RX_NODE, gpios)
#define LED_RX_PIN	DT_GPIO_PIN(LED_RX_NODE, gpios)
#define LED_RX_FLAGS	DT_GPIO_FLAGS(LED_RX_NODE, gpios)
#endif

#if DT_NODE_HAS_STATUS(GPIO_RSTN_NODE, okay)
#define GPIO_RSTN_LABEL DT_GPIO_LABEL(GPIO_RSTN_NODE, gpios)
#define GPIO_RSTN_PIN 0
// DT_GPIO_PIN(GPIO_RSTN_NODE, gpios)
#define GPIO_RSTN_FLAGS DT_GPIO_FLAGS(GPIO_RSTN_NODE, gpios)
#endif

struct k_thread coop_thread;

K_THREAD_STACK_DEFINE(coop_stack, STACKSIZE);

/*
 * @class cpp_semaphore
 * @brief Semaphore
 *
 * Class derives from the pure virtual semaphore class and
 * implements it's methods for the semaphore
 */
class cpp_semaphore: public semaphore {
protected:
	struct k_sem _sema_internal;
public:
	cpp_semaphore();
	virtual ~cpp_semaphore() {}
	virtual int wait(void);
	virtual int wait(int timeout);
	virtual void give(void);
};

/*
 * @brief cpp_semaphore basic constructor
 */
cpp_semaphore::cpp_semaphore()
{
	printk("Create semaphore %p\n", this);
	k_sem_init(&_sema_internal, 0, UINT_MAX);
}

/*
 * @brief wait for a semaphore
 *
 * Test a semaphore to see if it has been signaled.  If the signal
 * count is greater than zero, it is decremented.
 *
 * @return 1 when semaphore is available
 */
int cpp_semaphore::wait(void)
{
	k_sem_take(&_sema_internal, K_FOREVER);
	return 1;
}

/*
 * @brief wait for a semaphore within a specified timeout
 *
 * Test a semaphore to see if it has been signaled.  If the signal
 * count is greater than zero, it is decremented. The function
 * waits for timeout specified
 *
 * @param timeout the specified timeout in ticks
 *
 * @return 1 if semaphore is available, 0 if timed out
 */
int cpp_semaphore::wait(int timeout)
{
	return k_sem_take(&_sema_internal, K_MSEC(timeout));
}

/**
 *
 * @brief Signal a semaphore
 *
 * This routine signals the specified semaphore.
 *
 * @return N/A
 */
void cpp_semaphore::give(void)
{
	k_sem_give(&_sema_internal);
}

cpp_semaphore sem_main;
cpp_semaphore sem_coop;

void coop_thread_entry(void)
{
	struct k_timer timer;

	k_timer_init(&timer, NULL, NULL);

	while (1) {
		/* wait for main thread to let us have a turn */
		sem_coop.wait();

		/* say "hello" */
		printk("%s: Hello World!\n", __FUNCTION__);

		/* wait a while, then let main thread have a turn */
		k_timer_start(&timer, K_MSEC(SLEEPTIME), K_NO_WAIT);
		k_timer_status_sync(&timer);
		sem_main.give();
	}
}

void main(void)
{
	const struct device *led_tx;
	const struct device *rstn;
	const struct device *spi;
	int ret;

	// spi = device_get_binding("dw1000_spi");
	spi = device_get_binding("spi0");
	struct spi_config spi_cfg {
		.frequency = 2000000U,
        	.operation = SPI_WORD_SET(8) | SPI_TRANSFER_MSB | SPI_OP_MODE_MASTER,
    	};

	uint8_t tx_buf[8] = {0,0,0,0,0,0,0,0};
	uint8_t rx_buf[32];

	struct spi_buf spi_buf_tx[] = {
		{
			.buf = tx_buf,
			.len = sizeof(tx_buf)
		},
    	};

	struct spi_buf spi_buf_rx[] = {
		{
			.buf = rx_buf,
			.len = sizeof(rx_buf)
		},
	};

	struct spi_buf_set tx = {
		.buffers = spi_buf_tx,
		.count = 1
	};

	struct spi_buf_set rx = {
		.buffers = spi_buf_rx,
		.count = 9
	};

	tx_buf[0] = 0x0;
	spi_transceive(spi, &spi_cfg, &tx, &rx);
	printk("Got DW1000 DEVID: %02X%02X%02X%02X\n", rx_buf[4], rx_buf[3], rx_buf[2], rx_buf[1]);

	for(int i=0;i<rx.count;++i) {
		rx_buf[i] = 0x00;
	}
	tx_buf[0] = 0x1;
	spi_transceive(spi, &spi_cfg, &tx, &rx);
	printk("Got DW1000 EUID: %02X\n", *((uint64_t*)&rx_buf[1]));

	for(int i=0;i<rx.count;++i) {
		rx_buf[i] = 0x00;
	}
	tx_buf[0] = 0x3;
	spi_transceive(spi, &spi_cfg, &tx, &rx);
	printk("Got DW1000 PANID: %02X\n", *((uint32_t*)&rx_buf[1]));

	for(int i=0;i<rx.count;++i) {
		rx_buf[i] = 0x00;
	}
	tx_buf[0] = 0x4;
	spi_transceive(spi, &spi_cfg, &tx, &rx);
	uint32_t sys_cfg = *((uint32_t*)&rx_buf[1]);
	printk("sys_cfg: %08X\n", sys_cfg);
	if ((sys_cfg >> 9) & 1) {
		printk("HIRQ_POL enabled\n");
	} else {
		printk("HIRQ_POL disabled\n");
	}
	if ((sys_cfg >> 12) & 1) {
		printk("DIS_DRXB enabled\n");
	} else {
		printk("DIS_DRXB disabled\n");
	}

	for(int i=0;i<rx.count;++i) {
		rx_buf[i] = 0x00;
	}
	tx_buf[0] = 0x6;
	spi_transceive(spi, &spi_cfg, &tx, &rx);
	uint64_t sys_time = ((uint64_t)*((uint32_t*)&rx_buf[2]) << 8) + rx_buf[1];
	printk("SYS_TIME: %jX\n", sys_time);
	// printk("Got SYS_TIME: %02X%02X\n", *((uint32_t*)&rx_buf[1]), (uint8_t)rx_buf[5]);

	led_tx = device_get_binding(LED_TX_LABEL);
	ret = gpio_pin_configure(led_tx, LED_TX_PIN, GPIO_OUTPUT | LED_RX_FLAGS);
	gpio_pin_set(led_tx, LED_TX_PIN, (int)1);

	rstn = device_get_binding(GPIO_RSTN_LABEL);
	ret = gpio_pin_configure(rstn, GPIO_RSTN_PIN, GPIO_INPUT);
	int rstn_in = gpio_pin_get(rstn, GPIO_RSTN_PIN);
	// k_sleep(1);
	if (rstn_in) {
		printk("%s: GPIO RSTn is high!\n", __FUNCTION__);
	} else {
		printk("%s: GPIO RSTn is low!\n", __FUNCTION__);
	}
	struct k_timer timer;

	k_thread_create(&coop_thread, coop_stack, STACKSIZE,
			(k_thread_entry_t) coop_thread_entry,
			NULL, NULL, NULL, K_PRIO_COOP(7), 0, K_NO_WAIT);
	k_timer_init(&timer, NULL, NULL);

	while (1) {
		/* say "hello" */
		printk("%s: Hello World!\n", __FUNCTION__);

		/* wait a while, then let coop thread have a turn */
		k_timer_start(&timer, K_MSEC(SLEEPTIME), K_NO_WAIT);
		printk("%s: Hello World!\n", __FUNCTION__);
		k_timer_status_sync(&timer);
		sem_coop.give();

		/* Wait for coop thread to let us have a turn */
		sem_main.wait();
		gpio_pin_set(led_tx, LED_RX_PIN, (int)0);
	}
}
