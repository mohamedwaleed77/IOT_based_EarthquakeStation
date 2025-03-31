#include "MPU6050.h"
#include <string.h>
#include <math.h>
 // Function to initialize the MPU6050
HAL_StatusTypeDef MPU6050_Init(I2C_HandleTypeDef *hi2c) {
	volatile uint8_t check, data;

    // Check if MPU6050 is connected
    if (HAL_I2C_Mem_Read(hi2c, MPU6050_ADDR, WHO_AM_I_REG, 1, &check, 1, 1000) != HAL_OK) {
        return HAL_ERROR;
    }

    if (check != 0x68) {
        return HAL_ERROR;  // MPU6050 not found
    }

    // Wake up the MPU6050 (clear sleep mode bit)
    data = 0x00;
    if (HAL_I2C_Mem_Write(hi2c, MPU6050_ADDR, PWR_MGMT_1, 1, &data, 1, 1000) != HAL_OK) {
        return HAL_ERROR;
    }

    // Set accelerometer range to ±2g
    data = 0x00; //±2g:0x00 ,±4g:0x08 ,±8g:0x10 ,±16g: 0x18
    if (HAL_I2C_Mem_Write(hi2c, MPU6050_ADDR, ACCEL_CONFIG, 1, &data, 1, 1000) != HAL_OK) {
        return HAL_ERROR;
    }

    return HAL_OK;
}

float MPU6050_Read_Accel(I2C_HandleTypeDef *hi2c)
{
    uint8_t rawData[6];
    int16_t rawAx, rawAy, rawAz;
    float Ax, Ay, Az;

    // Read accelerometer data
    if (HAL_I2C_Mem_Read(hi2c, MPU6050_ADDR, ACCEL_XOUT_H, 1, rawData, 6, 100) != HAL_OK)
    {
        MPU6050_Init(hi2c);
        return -1.0;  // Return error value
    }

    // Convert raw data to acceleration (m/s²)
    rawAx = (int16_t)((rawData[0] << 8) | rawData[1]);
    rawAy = (int16_t)((rawData[2] << 8) | rawData[3]);
    rawAz = (int16_t)((rawData[4] << 8) | rawData[5]);

    Ax = ((float)rawAx / MPU6050_ACCEL_SENS_2G) * 9.81f;
    Ay = ((float)rawAy / MPU6050_ACCEL_SENS_2G) * 9.81f;
    Az = ((float)rawAz / MPU6050_ACCEL_SENS_2G) * 9.81f;

    // === Step 1: Compute Gravity Vector Magnitude ===
    float g_magnitude = sqrt(Ax * Ax + Ay * Ay + Az * Az);


    // Normalize gravity vector (unit vector)
    float gX = (Ax / g_magnitude) * 9.81f;
    float gY = (Ay / g_magnitude) * 9.81f;
    float gZ = (Az / g_magnitude) * 9.81f;

    // === Step 2: Remove Gravity from Acceleration ===
    float aX_noG = Ax - gX;
    float aY_noG = Ay - gY;
    float aZ_noG = Az - gZ;

    // Compute magnitude of true motion
    float motionMagnitude = sqrt(aX_noG * aX_noG + aY_noG * aY_noG + aZ_noG * aZ_noG);
    motionMagnitude-=0.55;
       if (motionMagnitude<0)return 0.0;
       // === Step 3: Apply Strict Noise Filtering ===


    return motionMagnitude;
}

