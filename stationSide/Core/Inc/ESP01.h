#ifndef ESP01_H
#define ESP01_H

#include "main.h"  // Change this based on your STM32 series
#include <stdbool.h>

#include <ESP01_SECRET_KEYS.h>

#define UDP_TARGET_IP   "192.168.1.108"
#define UDP_TARGET_PORT 5005  // Define the UDP port number
#define RST_PORT 		GPIOA
#define RST_PIN 		GPIO_PIN_0
extern UART_HandleTypeDef huart1;  // Use UART1

// Function prototypes
void ESP_Init(void);
void ESP_Send_Data(float data, int Station_ID);
void ESP_HARD_RESET(void);
HAL_StatusTypeDef WaitForResponse(const char *expected, uint32_t timeout);

#endif // __ESP01_H
