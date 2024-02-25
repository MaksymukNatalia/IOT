import sys
from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config
from typing import List

from domain.parking import Parking


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        parking_filename: str
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_data = None
        self.gps_data = None
        self.count = 0
        self.parking_filename=parking_filename
        self.parking_data = None
        pass

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        file = open(self.accelerometer_filename)
        self.accelerometer_data = reader(file)
        next(self.accelerometer_data)

        file2 = open(self.gps_filename)
        self.gps_data = reader(file2)
        next(self.gps_data)

        file3 = open(self.parking_filename)
        self.parking_data = reader(file3)
        next(self.parking_data)

    def read(self) -> List[AggregatedData]:
        """Метод повертає дані отримані з датчиків"""
        data_return = []

        ac = next(self.accelerometer_data)
        gp = next(self.gps_data)
        pa = next(self.parking_data)
        da = AggregatedData(
            Accelerometer(int(ac[0]), int(ac[1]), int(ac[2])),
            Gps(float(gp[0]), float(gp[1])),
            Parking(int(pa[0]), Gps(float(pa[1]), float(pa[2]))),
            datetime.now(),
            config.USER_ID)
        data_return.append(da)
        self.count+=1
        if self.count == 40:
            print("END")
            sys.exit()
        return da


    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
      #  .close()