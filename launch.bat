@echo off

REM Print number of CPUs
echo Number of CPUs:
WMIC CPU Get NumberOfCores

SET IMAGE_NAME=jokesta/warning
SET CONTAINER_NAME=app1

REM Check if the image exists locally
docker images "%IMAGE_NAME%" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Image %IMAGE_NAME% not found locally. Please pull the image before running the container.
    exit /b
)

FOR /F "tokens=*" %%A IN ('docker inspect --format "{{json .State.Running}}" %CONTAINER_NAME% 2^>nul') DO SET RUNNING=%%A

IF "%RUNNING%"=="true" (
    echo Container %CONTAINER_NAME% is already running. Stopping and removing it...
    docker stop %CONTAINER_NAME% >nul
    docker rm %CONTAINER_NAME% >nul
)

REM Function to start container
:start_container
FOR /F "tokens=*" %%B IN ('docker run -d -p 8000:8000 --name %CONTAINER_NAME% %IMAGE_NAME%') DO SET CONTAINER_ID=%%B

IF "%CONTAINER_ID%"=="" (
    echo Failed to start container. Performing system prune and retrying...
    docker system prune -a -f >nul
    goto start_container
)

echo Service is running at: 
echo http://localhost:8000

echo.
echo Press any key to exit...
pause >nul
