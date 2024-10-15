import datetime
import hashlib
import os
import random
import subprocess

import numpy as np
import pandas as pd
import pytils

from Azimuth import Azimuth
from CONFIG import NUM_OF_SERIES, ANGLE_MSE, GYRO_MSE, BASE_PATH


class VariantGenerator:

    def __init__(self, student_name: str, num_of_series=NUM_OF_SERIES):
        self.student_name = student_name.strip()
        self.num_of_series = num_of_series
        random.seed(self._get_hash())
        np.random.seed(self._get_hash())
        self.measured_data = []
        self.stable_error = self._get_stable_error()
        self._init_measured_data()

    def _get_hash(self):
        # hash_ = int(hashlib.sha256(self.student_name.encode("UTF-8")).hexdigest(), 16)
        hash_ = int(hashlib.sha256(self.student_name.encode("UTF-8")).hexdigest(), 16) % 10 ** 8
        return hash_

    def _get_mse_of_polygonometry(self, num_of_angles, angle_mse=ANGLE_MSE):
        return angle_mse * num_of_angles ** 0.5

    def _get_double_measurements(self):
        gyro_1 = Azimuth(mse=GYRO_MSE)
        gyro_2 = gyro_1.get_double_measurement(mse=GYRO_MSE)
        n = random.randint(5, 15)
        poly_mse = self._get_mse_of_polygonometry(num_of_angles=n)
        poly_azimuth = gyro_1.get_double_measurement(mse=poly_mse)
        # poly_azimuth.measured_azimuth += self.stable_error
        return {"Gyro_1": gyro_1,
                "Gyro_2": gyro_2,
                "Poly_Azimuth": poly_azimuth,
                "num_of_angles": n,
                }

    def _get_stable_error(self):
        return random.random() / 60 * 3

    def _init_measured_data(self):
        for _ in range(self.num_of_series):
            self.measured_data.append(self._get_double_measurements())

    def get_measure_df(self, to_str=False):
        df_lst = []
        for series in self.measured_data:
            gyro_1 = series["Gyro_1"].get_str_for_measurement(series["Gyro_1"].measured_azimuth) \
                        if to_str \
                        else series["Gyro_1"].measured_azimuth
            gyro_2 = series["Gyro_2"].get_str_for_measurement(series["Gyro_2"].measured_azimuth) \
                        if to_str \
                        else series["Gyro_2"].measured_azimuth
            poly_azimuth = series["Poly_Azimuth"].get_str_for_measurement(series["Poly_Azimuth"].measured_azimuth) \
                        if to_str \
                        else series["Poly_Azimuth"].measured_azimuth
            df_lst.append({"Gyro_1": gyro_1,
                           "Gyro_2": gyro_2,
                           "Poly_Azimuth": poly_azimuth,
                           "num_of_angles": series["num_of_angles"],
                           })
        return pd.DataFrame(df_lst, index=list(range(1, self.num_of_series + 1)))

    def _generate_template(self, variant_path):
        with open("templ1.txt", "rt") as file:
            templ1 = file.read()
        with open("templ2.txt", "rt") as file:
            templ2 = file.read()
        try:
            translit_name = pytils.translit.translify(self.student_name.strip())
        except ValueError:
            print(self.student_name)
            translit_name = "JD"
        with open(os.path.join(variant_path, 'template.tex'), "w") as file:
            file.write(templ1)
            # file.write(translit_name)
            file.write(r"}\n\lhead{")
            file.write("MMOMGI")
            file.write(templ2)

    def save_variant(self, base_path=BASE_PATH, students_group=""):
        variant_path = os.path.join(base_path, f"ММОМГИ_Двойные_Измерения_{datetime.datetime.now().year}",
                                    f"ММОМГИ_Двойные_Измерения_{students_group}")
        os.makedirs(variant_path, exist_ok=True)
        df = vg.get_measure_df(to_str=True)
        with open(os.path.join(variant_path, 'temp.md'), 'w') as f:
            f.write(df.to_markdown(index=True))

        def markdown_to_pdf(input_file, output_file, template_file=None):
            command = f"pandoc {input_file} -o {output_file} --pdf-engine=xelatex"
            if template_file:
                command += f" --template={template_file}"
            subprocess.run(command, shell=True)

        self._generate_template(variant_path)
        markdown_to_pdf(os.path.join(variant_path, 'temp.md'),
                        os.path.join(variant_path, f"{self.student_name.replace(" ", "_")}.pdf"),
                        os.path.join(variant_path, "template.tex"))

        os.remove(os.path.join(variant_path, 'temp.md'))
        os.remove(os.path.join(variant_path, 'template.tex'))

def create_variants_for_students_file(students_file, base_path=BASE_PATH):
    with (open(os.path.join(base_path, students_file), "rt", encoding="UTF-8") as file):
        for student in file:
            student_name, student_group = student.strip().split(";")
            vg = VariantGenerator(student_name)
            vg.save_variant(students_group=student_group)
            print(student_name, student_group)





if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name)

    for measure in vg.measured_data:
        print(measure)

    print(pd.DataFrame(vg.measured_data))

    print(vg.get_measure_df(to_str=True))

    df = vg.get_measure_df(to_str=True)

    # with open('output.txt', 'w') as f:
    #     f.write(df.to_string(index=True))

    # from tabulate import tabulate
    #
    # with open('output.txt', 'w') as f:
    #     f.write(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

    # with open('output.md', 'w') as f:
    #     f.write(df.to_markdown(index=True))

    # import subprocess


    # def markdown_to_pdf(input_file, output_file):
    #     command = f"pandoc {input_file} -o {output_file}"
    #     subprocess.run(command, shell=True)
    #
    #
    # # Пример использования
    # markdown_to_pdf('output.md', 'output.pdf')

    # vg.save_variant()

    create_variants_for_students_file("GG-21.csv")



