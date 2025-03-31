#include "ESP01.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "st7735.h"
#include "fonts.h"
#include "main.h"
extern IWDG_HandleTypeDef hiwdg;
#define RX_BUFFER_SIZE 128

// Sends an AT command and waits for the expected response
static HAL_StatusTypeDef SendCommand(const char *cmd, const char *expected, uint32_t timeout)
{
    char cmdBuffer[128];
    snprintf(cmdBuffer, sizeof(cmdBuffer), "%s\r\n", cmd);

    // Transmit the command over UART1
    HAL_UART_Transmit(&huart1, (uint8_t*)cmdBuffer, strlen(cmdBuffer), 1000);

    // Wait for the expected response (non-blocking, no retries)
    return WaitForResponse(expected, timeout);
}

// Waits for a response within a given timeout (no retries, returns immediately if no response)
HAL_StatusTypeDef WaitForResponse(const char *expected, uint32_t timeout)
{

    uint32_t tickstart = HAL_GetTick();
    uint8_t rxByte;
    char buffer[RX_BUFFER_SIZE];
    uint16_t index = 0;
    memset(buffer, 0, sizeof(buffer));
    while ((HAL_GetTick() - tickstart) < timeout)
    {
        if (HAL_UART_Receive(&huart1, &rxByte, 1, 100) == HAL_OK)
        {
            if (index < RX_BUFFER_SIZE - 1)
            {
                buffer[index++] = rxByte;
                buffer[index] = '\0';
                if (strstr(buffer, expected) != NULL)
                {


                	HAL_IWDG_Refresh(&hiwdg);
                    return HAL_OK;
                }
            }
        }
    }
    //ST7735_FillScreenFast(ST7735_WHITE);
    ST7735_WriteString(1, ESP_Y,buffer, Font_5x8, ST7735_RED, ST7735_BLACK);

    return HAL_TIMEOUT; // No retries, just return the result
}

// Initializes ESP without retries or reset

void ESP_HARD_RESET(){


	HAL_GPIO_WritePin(RST_PORT, RST_PIN, 0);
	HAL_Delay(50);
	HAL_GPIO_WritePin(RST_PORT, RST_PIN, 1);



}
void ESP_Init(void)
{

    	char cmd[128];
    	// Check if already connected to Wi-Fi
    	ST7735_WriteString(1, ESP_Y,"checking connection", Font_5x8, ST7735_GREEN, ST7735_BLACK);

    	if (SendCommand("AT+CWJAP?", "No AP", 500)!= HAL_OK){

            snprintf(cmd, sizeof(cmd), "AT+CIPSTART=\"UDP\",\"%s\",%d", UDP_TARGET_IP, UDP_TARGET_PORT);

            SendCommand(cmd, "OK", 1500);
            if (SendCommand("AT", "OK", 100)==HAL_OK){
            	ST7735_FillRectangleFast(0, ESP_Y, 128,45, ST7735_BLACK);
            	ST7735_WriteString(20,ESP_Y,"ESP IS WORKING...", Font_5x8, ST7735_GREEN, ST7735_BLACK);
            	return;
            }
            else{
            	ST7735_FillRectangleFast(0, ESP_Y, 128,45, ST7735_BLACK);
            	ST7735_WriteString(1,ESP_Y,"ESP ERROR...", Font_5x8, ST7735_WHITE, ST7735_BLACK);
            	HAL_Delay(10000);
            	NVIC_SystemReset();
            }


    	}

        // Set Wi-Fi mode to station mode
    	ST7735_FillRectangleFast(0, ESP_Y, 128,45, ST7735_BLACK);
    	ST7735_WriteString(1,ESP_Y,"CONNECTING...", Font_5x8, ST7735_WHITE, ST7735_BLACK);

        SendCommand("AT+CWMODE=1", "OK", 1500);

        // Attempt to connect
        snprintf(cmd, sizeof(cmd), "AT+CWJAP=\"%s\",\"%s\"", WIFI_SSID, WIFI_PASSWORD);

        SendCommand(cmd, "OK", 15000);

        // Attempt to start UDP connection (one-shot)
        snprintf(cmd, sizeof(cmd), "AT+CIPSTART=\"UDP\",\"%s\",%d", UDP_TARGET_IP, UDP_TARGET_PORT);

        SendCommand(cmd, "OK", 3000);

        if (SendCommand("AT", "OK", 100)==HAL_OK){
        	ST7735_FillRectangleFast(0, ESP_Y, 128,45, ST7735_BLACK);
        	ST7735_WriteString(20,ESP_Y,"ESP IS WORKING...", Font_5x8, ST7735_GREEN, ST7735_BLACK);
        }
        else{
        	ST7735_FillRectangleFast(0, ESP_Y, 128,45, ST7735_BLACK);
        	ST7735_WriteString(1,ESP_Y,"ESP ERROR...", Font_5x8, ST7735_WHITE, ST7735_BLACK);
        	HAL_Delay(10000);
        	NVIC_SystemReset();
        }
}

// Sends real-time data over UDP (no retry, no waiting)
void ESP_Send_Data(float data, int Station_ID)
{
    char payload[64];
    snprintf(payload, sizeof(payload), "Station %d: %.8f", Station_ID, data);
    uint16_t len = strlen(payload);

    // Send AT+CIPSEND command
    char cmd[32];
    snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%d", len);

    if (SendCommand(cmd, ">", 500) == HAL_OK)
    {
        // Send the payload immediately
    	//ST7735_WriteString(10,ESP_Y+10,payload, Font_5x8, ST7735_GREEN, ST7735_BLACK);
        HAL_UART_Transmit(&huart1, (uint8_t*)payload, len, HAL_MAX_DELAY);
    }
    else{
    	ESP_Init();
    }
}
