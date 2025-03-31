#ifndef MPU6050_H
#define MPU6050_H

#include "stm32f1xx_hal.h"  // Adjust for your MCU family if needed
#include <stdint.h>

// MPU6050 I2C Address
#define MPU6050_ADDR 0x68 << 1  // Shifted for HAL (7-bit address is 0x68)

// MPU6050 Registers
#define WHO_AM_I_REG     0x75
#define PWR_MGMT_1       0x6B

#define ACCEL_CONFIG 	 0x1C
#define ACCEL_XOUT_H     0x3B


#define MPU6050_ACCEL_SENS_2G  16384.0  // LSB/g for ±2g full scale
#define MPU6050_ACCEL_SENS_4G  8192.0
#define MPU6050_ACCEL_SENS_8G  4096.0
#define MPU6050_ACCEL_SENS_16G  2048.0
// Struct to store acceleration values
typedef struct {
    float Ax;
    float Ay;
    float Az;
} MPU6050_Data_t;

// Function prototypes
HAL_StatusTypeDef MPU6050_Init(I2C_HandleTypeDef *hi2c);
float MPU6050_Read_Accel(I2C_HandleTypeDef *hi2c);

#endif
