from sqlmodel import Session

from constants.calculation.calculation_types import WindowCalculations
from constants.calculation.category import WindowCategories
from models import PerformanceDataCategory, PerformanceDataCalculation


def populate_performance_data(db_session: Session, ) -> None:
    for item in WindowCategories.VALUES:
        category_obj = PerformanceDataCategory(
            id=item.value,
            name=item.name,
        )
        db_session.add(category_obj)

    for calculation in WindowCalculations.VALUES:
        calculation_obj = PerformanceDataCalculation(
            id=calculation.value,
            name=calculation.name,
            description=calculation.description,
            data_category_id=calculation.category.value,
        )
        db_session.add(calculation_obj)

    print("Adding categories and calculations")
