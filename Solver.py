import datetime
import os
import subprocess
from copy import copy

from Azimuth import Azimuth
from CONFIG import GYRO_MSE, ANGLE_MSE, BASE_PATH


class Solver:

    def __init__(self, variant_generator, mse_poly_0=ANGLE_MSE, mse_gyro_0=GYRO_MSE):
        self.variant_generator = variant_generator
        self.df = variant_generator.get_measure_df(to_str=False)
        self.prepare_df_data()
        self.df_1 = None
        self.df_2 = None
        self.mse_poly_0 = mse_poly_0
        self.mse_gyro_0 = mse_gyro_0
        self.mu_0 = self.mse_gyro_0 / 2 ** 0.5
        self.mu = None
        self.gyro_mse = None

    def prepare_df_data(self):
        self.df["Gyro_1"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in self.df["Gyro_1"]]
        self.df["Gyro_2"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in self.df["Gyro_2"]]
        self.df["Poly_Azimuth"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in self.df["Poly_Azimuth"]]

        self.df["Gyro_1"] = [self.get_angle_from_str(azimuth) for azimuth in self.df["Gyro_1"]]
        self.df["Gyro_2"] = [self.get_angle_from_str(azimuth) for azimuth in self.df["Gyro_2"]]
        self.df["Poly_Azimuth"] = [self.get_angle_from_str(azimuth) for azimuth in self.df["Poly_Azimuth"]]


    def solve_variant(self, base_path=BASE_PATH, students_group=""):
        self.solve_the_first_part()
        self.solve_the_second_part()
        self.print_part_1_to_pdf(base_path=base_path, students_group=students_group)
        self.print_part_2_to_pdf(base_path=base_path, students_group=students_group)

    def solve_the_first_part(self):
        self.df_1 = self.df.copy(deep=True)
        self.df_1 = self.df_1.drop(["Poly_Azimuth", "num_of_angles"], axis=1)
        self.df_1["d"] = (self.df_1["Gyro_2"] - self.df_1["Gyro_1"]) * 3600
        self.df_1["dd"] = self.df_1["d"] ** 2
        self.df_1["$|d|$"] = abs(self.df_1["d"])
        if abs(self.df_1["d"].sum()) <= 0.25 * self.df_1["$|d|$"].sum():
            sum_of_dd = self.df_1["dd"].sum()
            gyro_mse = (sum_of_dd / (2 * len(self.df_1))) ** 0.5
        else:
            self.df_1["d\'"] = self.df_1["d"] - self.df_1["d"].sum() / len(self.df_1)
            self.df_1["d\'d\'"] = self.df_1["d\'"] ** 2
            sum_of_dd = self.df_1["d\'d\'"].sum()
            gyro_mse = (sum_of_dd / (2 * (len(self.df_1) - 1))) ** 0.5
        gyro_mse = Azimuth.get_str_for_measurement(gyro_mse / 3600)
        self.gyro_mse = gyro_mse

    def solve_the_second_part(self):
        self.df_2 = self.df.copy(deep=True)
        self.df_2["Gyro_AVR"] = (self.df_2["Gyro_2"] + self.df_2["Gyro_1"]) / 2
        self.df_2 = self.df_2.drop(["Gyro_1", "Gyro_2"], axis=1)
        self.df_2 = self.df_2[["Gyro_AVR", "Poly_Azimuth", "num_of_angles"]]
        self.df_2["mse_poly"] = self.mse_poly_0 * self.df_2["num_of_angles"] ** 0.5
        self.df_2["p_gyro"] = 1
        self.df_2["p_poly"] = (self.mu_0 ** 2) / (self.df_2["mse_poly"] ** 2)
        self.df_2["p_d"] = (self.df_2["p_gyro"] * self.df_2["p_poly"]) / (self.df_2["p_gyro"] + self.df_2["p_poly"])
        self.df_2["d"] = (self.df_2["Poly_Azimuth"] - self.df_2["Gyro_AVR"]) * 3600
        self.df_2["$d\\sqrt{p_d}$"] = self.df_2["d"] * self.df_2["p_d"] ** 0.5
        self.df_2["$\\|d\\sqrt{p_d}\\|$"] = abs(self.df_2["$d\\sqrt{p_d}$"])
        self.df_2["pd"] = self.df_2["d"] * self.df_2["p_d"]

        if abs(self.df_2["$d\\sqrt{p_d}$"].sum()) <= 0.25 * self.df_2["$\\|d\\sqrt{p_d}\\|$"].sum():
            self.df_2["$p_ddd$"] = self.df_2["$d\\sqrt{p_d}$"] ** 2
            sum_of_pdd = self.df_2["$p_ddd$"].sum()
            mu = (sum_of_pdd / (len(self.df_2))) ** 0.5
        else:
            d_sist = self.df_2["pd"].sum() / self.df_2["p_d"].sum()
            self.df_2["d\'"] = self.df_1["d"] - d_sist
            self.df_2["$p_dd\'d\'$"] = self.df_2["p_d"] * self.df_2["d\'"] ** 2
            sum_of_dd = self.df_2["$p_dd\'d\'$"].sum()
            mu = (sum_of_dd / (2 * (len(self.df_2) - 1))) ** 0.5
        mu = Azimuth.get_str_for_measurement(mu / 3600)
        self.mu = mu
        print(self.df_2)
        print(self.mu_0, self.mu)

    @staticmethod
    def get_angle_from_str(angle_str: str):
        degree, min_sec = angle_str.split("°")
        minutes, seconds = min_sec.split("'")
        degree = int(degree)
        minutes = int(minutes)
        seconds = int(seconds[:-1])
        azimuth = degree + minutes / 60 + seconds / 3600
        return azimuth

    def print_part_1_to_pdf(self, base_path, students_group):
        self.solve_the_first_part()
        df = self.df_1.copy(deep=True)
        df["Gyro_1"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in df["Gyro_1"]]
        df["Gyro_2"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in df["Gyro_2"]]

        sum_of_d = df["d"].sum()
        sum_of_abs_d = df["$|d|$"].sum()
        check_str_1 = "\n\n$$ " + str(round(abs(sum_of_d), 3)) + " \\le 0.25 \\cdot " + str(round(sum_of_abs_d, 3)) + " $$"
        check_str_2 = "\n\n$$ " + str(round(abs(sum_of_d), 3)) + " \\le " + str(round(0.25*sum_of_abs_d, 3)) + " $$"

        stab_err_str = "\n\n$$ \\frac{[d]}{n} = " + str(round(sum_of_d / len(self.df_1), 3)) + " $$"
        gyro_mse = self.gyro_mse.replace("°", "^\\circ")
        mu_str = "\n\n$$ \\mu = " + str(gyro_mse) + " $$"

        variant_path = os.path.join(base_path, f"ММОМГИ_Двойные_Измерения_{datetime.datetime.now().year}",
                                    "Решение",
                                    f"ММОМГИ_Двойные_Измерения_{students_group}",
                                    f"{self.variant_generator.student_name.replace(" ", "_")}")
        os.makedirs(variant_path, exist_ok=True)
        with open(os.path.join(variant_path, 'temp.md'), 'w') as f:
            f.write(df.to_markdown(index=True))
            f.write("\n\n")
            f.write(df.sum().drop(["Gyro_1", "Gyro_2"]).to_markdown(index=True))
            f.write(check_str_1)
            f.write(check_str_2)
            f.write(stab_err_str)
            f.write(mu_str)

        # self.variant_generator.generate_template(variant_path)
        self.markdown_to_pdf(os.path.join(variant_path, 'temp.md'),
                             os.path.join(variant_path, f"part_1.pdf"),
                             "template.tex")

        os.remove(os.path.join(variant_path, 'temp.md'))
        # os.remove(os.path.join(variant_path, 'template.tex'))

    def print_part_2_to_pdf(self, base_path, students_group):
        self.solve_the_second_part()
        df = self.df_2.copy(deep=True)
        df["Gyro_AVR"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in df["Gyro_AVR"]]
        df["Poly_Azimuth"] = [Azimuth.get_str_for_measurement(azimuth) for azimuth in df["Poly_Azimuth"]]

        sum_of_d_sq_p = df["$d\\sqrt{p_d}$"].sum()
        sum_of_abs_d_sq_p = df["$\\|d\\sqrt{p_d}\\|$"].sum()
        check_str_1 = "\n\n$$ " + str(round(abs(sum_of_d_sq_p), 3)) + " \\le 0.25 \\cdot " + str(
            round(sum_of_abs_d_sq_p, 3)) + " $$"
        check_str_2 = "\n\n$$ " + str(round(abs(sum_of_d_sq_p), 3)) + " \\le " + str(round(0.25 * sum_of_abs_d_sq_p, 3)) + " $$"

        stab_err_str = "\n\n$$ \\frac{[pd]}{[p]} = " + str(round(self.df_2["pd"].sum() / self.df_2["p_d"].sum(), 3)) + " $$"
        mu = copy(self.mu).replace("°", "^\\circ")
        mu_str = "\n\n$$ \\mu = " + str(mu) + " $$"

        variant_path = os.path.join(base_path, f"ММОМГИ_Двойные_Измерения_{datetime.datetime.now().year}",
                                    "Решение",
                                    f"ММОМГИ_Двойные_Измерения_{students_group}",
                                    f"{self.variant_generator.student_name.replace(" ", "_")}")
        os.makedirs(variant_path, exist_ok=True)
        with open(os.path.join(variant_path, 'temp.md'), 'w') as f:
            f.write(df.to_markdown(index=True))
            f.write(check_str_1)
            f.write(check_str_2)
            f.write(stab_err_str)
            f.write(mu_str)

    @staticmethod
    def markdown_to_pdf(input_file, output_file, template_file=None):
        command = f"pandoc {input_file} -o {output_file} --pdf-engine=xelatex"
        if template_file:
            command += f" --template={template_file}"
        subprocess.run(command, shell=True)



if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name)
    solver = Solver(vg)
    solver.solve_variant()