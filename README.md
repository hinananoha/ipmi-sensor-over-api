# ipmi-sensor-over-api
Get sensor data over HTTP API using local IPMI

## Description
This is python API server for sensor data using local IPMI data.
This system can use for Zabbix server(HTTP Agent item).

## Requirement
- can use IPMI and access from local without password
  - after install openipmi, run `sudo ipmitool sensor`. If sensor data can get, this requirement is OK.
- Ubuntu, Debian, etc...(Debian-base OS)
- package:
  - openipmi
  - git
  - python3
  - python3-pip
    - flask
    - flask_restful
- If you run this API over wsgi, following packages also needed (RECOMMENDED)  
  - apache2, apache2-dev
  - libapache2-mod-wsgi-py3
  - python3-pip
    - mod_wsgi

## Test environment
- Ubuntu Server 18.04 LTS/ Ubuntu Server 20.04 LTS
- Python 3.6.9/3.8.5
- Hardware:
  - A.T.Works, Inc. Quad Beagle ZG+
  - NEC Express5800/E120d-1
- Zabbix Server 5.0/5.2 (for Zabbix Template)

## Installation(Common: Required this step all type)
### 1. Install packages
```
# apt update
# apt install openipmi python3 python3-pip
```
### 2. Install python modules
```
# pip3 install flask flask_restful
```
### 3. Get sensor data for test
```
# ipmitool sensor
```
If this command is runnning collect, displayed following output(example):
```
+5V              | 5.040      | Volts      | ok    | na        | 4.760     | 4.800     | 5.200     | 5.240     | na
+5VSB            | 5.040      | Volts      | ok    | na        | 4.760     | 4.800     | 5.200     | 5.240     | na
+12V             | 12.000     | Volts      | ok    | na        | 10.800    | 11.200    | 12.400    | 12.800    | na
+VCORE           | 0.680      | Volts      | ok    | na        | 0.560     | na        | na        | 1.400     | na
+3.3V            | 3.320      | Volts      | ok    | na        | 3.080     | 3.120     | 3.560     | 3.720     | na
CPU FAN          | 2800.000   | RPM        | ok    | na        | 490.000   | 980.000   | na        | na        | na
SYS FAN          | 4480.000   | RPM        | ok    | na        | 980.000   | 1960.000  | na        | na        | na
AUX FAN          | 4550.000   | RPM        | ok    | na        | 980.000   | 1960.000  | na        | na        | na
CPU Temp         | 38.000     | degrees C  | ok    | na        | na        | na        | na        | 85.000    | 92.000
System TEMP      | 49.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 70.000
AUX TEMP         | 49.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 70.000
```
  - IMPORTANT: If command execution time is long, you must kill this command after you get data that you needed.
    - (When this command runnning on enterprise server, this command can many data but runnning time is many mnay long. If you want to only Voltage/Fan speed/Temperature, you stop this command after display these data. Only these(Voltage/Fan speed/Temperature) data, probability run command and wait only 5~10 seconds, after kill this command.)
### 4. Prepare data collector
```
# mkdir /var/cache/ipmi-sensors/
# touch /var/cache/ipmi-sensors/sensor_data.txt
# chmod 644 /var/cache/ipmi-sensors/sensor_data.txt
```
### 5. Set data corrector using cron THAT ROOT PRIVILEDGE
```
# crontab -e
```
you insert this entry on root crontab:
```
*/1 * * * * ipmitool sensor > /var/cache/ipmi-sensors/sensor_data.txt
```
- If this command's execution time is long (you check previous step), add `timeout -s INT (timeout-seconds)` before this entry.
  - example (this example's timeout is 5 seconds):
```
*/1 * * * * timeout -s INT 5 ipmitool sensor > /var/cache/ipmi-sensors/sensor_data.txt
```
### 6. Check crontab
If runnning crontab, sensor data is wrote at `/var/cache/ipmi-sensors/sensor_data.txt`.
After 1 minutes that insert crontab, you check this file.
### 7. Clone this repository and runnnig API server
```
$ git clone https://github.com/hinananoha/ipmi-sensor-over-api.git
$ cd ipmi-sensor-over-api
$ python3 ipmi_sensor_server.py
```
### 8. Get sensor items (using another terminal/machine)
```
$ curl http://(python-running-machine-ip-address):(runnning-port)/sensors
```
Response example show after Usage section.

## Instllation (using WSGI - after finished step 8)
### 9. Install additional packages
```
# apt install apache2 apache2-dev libapache2-mod-wsgi-py3
# pip3 install mod_wsgi
```
### 10. Create API script directory and extract this repository files
```
# mkdir /var/www/flask/
# cd /var/www/flask/
# git clone https://github.com/hinananoha/ipmi-sensor-over-api.git .
# cd ../
# chown -R www-data:www-data flask/
```
### 10. Add sites config on apach2
```
# cd /var/www/flask/
# cp flask.conf /etc/apache2/sites-available/.
# a2ensite flask
```
If you want to runnning this API server on other port (default:3002), you modify this (flask.conf) file:
```diff
- <VirtualHost *:3002>
+ <VirtualHost *:(your-port)> 
```
### 11. Modify apache settings
Add this API port on `/etc/apache2/ports.conf`.
```diff
--- /etc/apache2/ports.conf.default     2021-05-09 05:46:23.266808939 +0000
+++ /etc/apache2/ports.conf     2021-05-09 05:46:37.314129602 +0000
@@ -3,6 +3,7 @@
 # /etc/apache2/sites-enabled/000-default.conf

 Listen 80
+Listen 3002

 <IfModule ssl_module>
        Listen 443
```
After this, set Hostname settings
```
# echo ServerName $HOSTNAME > /etc/apache2/conf-available/fqdn.conf
# a2enconf fqdn
```
### 12. Running API server
```
# systemctl restart apache2.service
```
### 13. Get sensor items
```
$ curl http://localhost:3002/sensors
```

## Usage
### API Response data (sample)
```json
{
  "sensors": {
    "+5V": {
      "value": 5.04,
      "unit": "Volts",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 4.76,
          "warn": 4.8
        },
        "max": {
          "warn": 5.2,
          "crit": 5.24,
          "fatal": null
        }
      }
    },
    "+5VSB": {
      "value": 5.04,
      "unit": "Volts",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 4.76,
          "warn": 4.8
        },
        "max": {
          "warn": 5.2,
          "crit": 5.24,
          "fatal": null
        }
      }
    },
    "+12V": {
      "value": 12.0,
      "unit": "Volts",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 10.8,
          "warn": 11.2
        },
        "max": {
          "warn": 12.4,
          "crit": 12.8,
          "fatal": null
        }
      }
    },
    "+VCORE": {
      "value": 0.72,
      "unit": "Volts",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 0.56,
          "warn": null
        },
        "max": {
          "warn": null,
          "crit": 1.4,
          "fatal": null
        }
      }
    },
    "+3.3V": {
      "value": 3.32,
      "unit": "Volts",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 3.08,
          "warn": 3.12
        },
        "max": {
          "warn": 3.56,
          "crit": 3.72,
          "fatal": null
        }
      }
    },
    "CPU FAN": {
      "value": 2870.0,
      "unit": "RPM",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 490.0,
          "warn": 980.0
        },
        "max": {
          "warn": null,
          "crit": null,
          "fatal": null
        }
      }
    },
    "SYS FAN": {
      "value": 4550.0,
      "unit": "RPM",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 980.0,
          "warn": 1960.0
        },
        "max": {
          "warn": null,
          "crit": null,
          "fatal": null
        }
      }
    },
    "AUX FAN": {
      "value": 4550.0,
      "unit": "RPM",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": 980.0,
          "warn": 1960.0
        },
        "max": {
          "warn": null,
          "crit": null,
          "fatal": null
        }
      }
    },
    "CPU Temp": {
      "value": 41.0,
      "unit": "degrees C",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": null,
          "warn": null
        },
        "max": {
          "warn": null,
          "crit": 85.0,
          "fatal": 92.0
        }
      }
    },
    "System TEMP": {
      "value": 49.0,
      "unit": "degrees C",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": null,
          "warn": null
        },
        "max": {
          "warn": null,
          "crit": 60.0,
          "fatal": 70.0
        }
      }
    },
    "AUX TEMP": {
      "value": 49.0,
      "unit": "degrees C",
      "status": "ok",
      "thresholds": {
        "min": {
          "fatal": null,
          "crit": null,
          "warn": null
        },
        "max": {
          "warn": null,
          "crit": 60.0,
          "fatal": 70.0
        }
      }
    }
  }
}
```
### If you want to use Zabbix
Import zabbix template `IPMI-over-HTTP.{xml,json,yaml}` from this repository (in `zabbix-template` directory).
This template name is **Template App IPMI Sensors via HTTP Agent**.
After import, link this template that you want to monitoring and edit macro that following:
  - {$API_SERVER_URL} : Your API Server URL (If you imprement using default, http://`<API-server-IP>`:3002/sensors)

This template is used LLD(Low Level Discovery), so create sensor items automatically.

## Author
author: hinananoha
