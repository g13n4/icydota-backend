from sqlmodel import Session

from helpers import get_id_dict
from models.performance import PerformanceWindowCalculationCategory, PerformanceWindowCalculationType


def create_performance_data(db_session: Session, ) -> None:
    category_dict = get_id_dict(db_session, PerformanceWindowCalculationCategory)
    calculation_dict = get_id_dict(db_session, PerformanceWindowCalculationType)

    for item in PerformanceWindowCalculationCategory.const.VALUES:
        if (category_obj := category_dict.get(item.value, None)):
            category_obj.name = item.name
        else:
            category_obj = PerformanceWindowCalculationCategory(
                id=item.value,
                name=item.name,
            )
        db_session.add(category_obj)

    for calculation in PerformanceWindowCalculationType.const.VALUES:
        if (calculation_obj := calculation_dict.get(calculation.db_id, None)):
            calculation_obj.name = calculation_obj.name
            calculation_obj.description = calculation.description
            calculation_obj.calc_category_id = calculation.category.value

        else:
            calculation_obj = PerformanceWindowCalculationType(
                id=calculation.db_id,
                name=calculation.name,
                description=calculation.description,
                calc_category_id=calculation.category.value,
            )
        db_session.add(calculation_obj)

    print("Adding categories and calculations")
