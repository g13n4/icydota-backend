from models.performance import PerformanceTotalData


class TotalPerformanceProcessor:

    @staticmethod
    def comparison_data_objs_to_ptd(cmd_obj: PerformanceTotalData, cms_obj: PerformanceTotalData, flat: bool) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            comparandum_value = getattr(cmd_obj, field)
            comparans_value = getattr(cms_obj, field)
            if comparandum_value is None or comparans_value is None:
                pass
            else:
                if flat:
                    value = comparandum_value - comparans_value
                else:
                    value = comparandum_value / comparans_value
                setattr(PTD_obj, field, value)

        return PTD_obj


    @staticmethod
    def reduce_total_objs(objects: list[PerformanceTotalData]) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            field_value = 0
            field_counter = 0
            for total_obj in objects:
                obj_value = getattr(total_obj, field)
                if obj_value is None:
                    pass
                else:
                    field_value += obj_value
                    field_counter += 1

            if field_value is not None:
                setattr(PTD_obj, field, field_value / field_counter)

        return PTD_obj
