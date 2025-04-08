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
                    value = comparandum_value - comparans_value
                else:
                    value = decimal_division(comparandum_value, comparans_value)
                setattr(PTD_obj, field.name, value)

        return PTD_obj


    @staticmethod
    def reduce_total_objs(
            total_objects: list[PerformanceTotalData],
            *,
            mode: str = "avg",
    ) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            field_value = 0
            field_counter = 0
            for total_obj in total_objects:
                this_obj_value = getattr(total_obj, field.name)
                if this_obj_value is None:
                    pass
                else:
                    field_value += this_obj_value
                    field_counter += 1

            if field_counter:
                match mode:
                    case "avg":
                        setattr(PTD_obj, field.name, decimal_division(field_value, field_counter))
                    case "sum":
                        setattr(PTD_obj, field.name, field_value)
                    case _:
                        raise ValueError(f"{mode} mode does not exist for totals reducing!")

        return PTD_obj


    @staticmethod
    def create_object_from_dict(data: dict) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            value = data[field.name]
            setattr(PTD_obj, field.name, value)

        return PTD_obj
