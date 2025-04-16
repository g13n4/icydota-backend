from decimal import Decimal

from models.performance import PerformanceTotalData
from modules.processors.helpers import decimal_division


class TotalPerformanceProcessor:

    @staticmethod
    def comparison_data_objs_to_ptd(
            cmd_obj: PerformanceTotalData,
            cms_obj: PerformanceTotalData,
            flat: bool,
    ) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            comparandum_value = getattr(cmd_obj, field.name)
            comparans_value = getattr(cms_obj, field.name)
            if comparandum_value is None or comparans_value is None:
                pass
            else:
                if flat:
                    value = Decimal(comparandum_value) - Decimal(comparans_value)
                else:
                    value = decimal_division(comparandum_value, comparans_value, bool_normalize=field.pseudo_bool)
                setattr(PTD_obj, field.name, value)

        return PTD_obj


    @staticmethod
    def reduce_total_objs(
            total_objects: list[PerformanceTotalData],
            *,
            mode: str = "avg",
    ) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field_item in PerformanceTotalData.const.VALUES:
            field_value = 0
            field_counter = 0
            for total_obj in total_objects:
                this_obj_value = getattr(total_obj, field_item.name)
                if this_obj_value is None:
                    continue
                else:
                    field_value += this_obj_value
                    field_counter += 1

            if field_counter:
                if field_item.pseudo_bool:
                    # normalize it
                    setattr(PTD_obj, field_item.name, decimal_division(field_value, field_counter, bool_normalize=True))
                elif mode == "avg":
                    setattr(PTD_obj, field_item.name, decimal_division(field_value, field_counter))
                elif mode == "sum":
                    setattr(PTD_obj, field_item.name, field_value)
                else:
                    raise ValueError(f"{mode} mode does not exist for totals reducing!")

        return PTD_obj


    @staticmethod
    def create_object_from_dict(data: dict) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            value = data[field.name]
            setattr(PTD_obj, field.name, value)

        return PTD_obj
