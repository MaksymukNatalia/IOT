import sys
from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config
from typing import List

class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_data = None
        self.gps_data = None
        self.count = 0
        pass
    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        file = open(self.accelerometer_filename)
        self.accelerometer_data = reader(file)
        print(next(self.accelerometer_data))

        file2 = open(self.gps_filename)
        self.gps_data = reader(file2)
        print(next(self.gps_data))

    def read(self) -> List[AggregatedData]:
        """Метод повертає дані отримані з датчиків"""
        data_return = []

        ac = next(self.accelerometer_data)
        gp = next(self.gps_data)
        da = AggregatedData(
            Accelerometer(int(ac[0]), int(ac[1]), int(ac[2])),
            Gps(float(gp[0]), float(gp[1])),
            datetime.now(),
            config.USER_ID)
        data_return.append(da)
        self.count+=1
        if self.count == 125:
            print("********")
            sys.exit()
        return da




    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
      #  .close()