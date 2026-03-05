

**One-line purpose:** CMakeList files and config PSRAM
**Short summary:** 
**Agent:** archived

---

**CMakeList.txt** (project level)
in root and in main
root: defineerd het esp-idf project
- minimale versie van CMake
- esp-idf build system (tools path)
- project naam
- configureert build options
```C
# The following five lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
# "Trim" the build. Include the minimal set of components, main, and anything it depends on.
idf_build_set_property(MINIMAL_BUILD ON)
project(gv2-lilygo)
```

**main/CMakeList.txt** (component level)
- source files
- incl directories
- declareerd component dependencies (drive, esp-dl, camera, etc)
```C
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES driver)
```

# maak basic main.c file
```C
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "main";

void app_main(void)
{
    ESP_LOGI(TAG, "ESP-OD project started");
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        ESP_LOGI(TAG, "Running...");
    }
}
```

test met 
```sh
idf.py build
```
dit maakt
- sdkconfig
- build/
- compiles project
# configureer de ESP32-S3
```sh
idf.py set-target esp32s3
```

### Permanent fix: configure the extension (one-time)
- Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)
- Type: "ESP-IDF: Configure ESP-IDF extension"
- In the wizard:
	- Choose "Use existing setup" (since ESP-IDF is already installed)
	- Set ESP-IDF path: ~/esp/esp-idf-v5.5.1 or /Users/md/esp/esp-idf-v5.5.1
	- Select target: esp32s3
	- Tools path: /Users/md/Developer/esp/tools (should auto-detect)

check with idf.py --version

the idf.py build

sdkconfig configureren voor de juiste chip
```sh
idf.py set-target esp32s3
```
gevolgd door idf.py build

show target
```
grep CONFIG_IDF_TARGET sdkconfig
```
moet esp32-s3 zijn
# dependencies toevoegen
```sh
idf.py add-dependency "espressif/esp-dl"
idf.py add-dependency "espressif/esp32-camera"
```

# update main/CMakeLists.txt
```sh
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES driver esp-dl esp32_camera)
```
idf.py build

# config PSRAM
```sh
   idf.py menuconfig
```
SP RAM
octal mode
8-MHZ
s
q
idf.py build


