import typing
from decimal import Decimal

from constants.performance.total.processing_options import TotalTeamProcessingOption
from models.performance import PerformanceTotalData
from modules.processors.helpers import decimal_division
from utils import to_dec
from utils.helpers import is_invalid_value


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
            comparison_mode: bool,
    ) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field_item in PerformanceTotalData.const.VALUES:
            field_name = field_item.name
            field_value = 0
            field_counter = 0
            field_not_none = None
            for total_obj in total_objects:
                this_obj_value = getattr(total_obj, field_name)
                if this_obj_value is None:
                    continue
                else:
                    if field_not_none is None or (field_not_none is not None and field_not_none < this_obj_value):
                        field_not_none = this_obj_value

                    field_value += this_obj_value
                    field_counter += 1

            if field_counter:
                if comparison_mode:
                    setattr(PTD_obj, field_name, decimal_division(field_value, field_counter))
                else:
                    match field_item.team_processing_option:
                        case TotalTeamProcessingOption.CEIL:
                            field_value = 1 if field_value > 0 else 0
                        case TotalTeamProcessingOption.BIGGEST:
                            field_value = field_not_none
                        case TotalTeamProcessingOption.AVERAGE:
                            field_value = field_value / field_counter


                    if field_item.pseudo_bool and not field_item.team_processing_option:
                        # normalize it
                        setattr(
                            PTD_obj,
                            field_name,
                            decimal_division(field_value, field_counter, bool_normalize=True)
                            )
                    else:
                        setattr(PTD_obj, field_name, field_value)

        return PTD_obj


    @staticmethod
    def create_object_from_dict(data: dict) -> PerformanceTotalData:
        PTD_obj = PerformanceTotalData()

        for field in PerformanceTotalData.const.VALUES:
            value = data[field.name]
            if is_invalid_value(value):
                value = None
            elif isinstance(field.value_type, typing._AnnotatedAlias):
                value = to_dec(value)
            elif field.value_type is typing.Optional[int]:
                value = int(value)
            else:
                raise TypeError("Value has an unknown type!")

            setattr(PTD_obj, field.name, value)

        return PTD_obj
