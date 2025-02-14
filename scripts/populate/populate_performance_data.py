from sqlmodel import Session

from models.performance import PerformanceDataCalculationCategory, PerformanceDataCalculation


def create_performance_data(db_session: Session, ) -> None:
    for item in PerformanceDataCalculationCategory.const.VALUES:
        category_obj = PerformanceDataCalculationCategory(
            id=item.value,
            name=item.name,
        )
        db_session.add(category_obj)

    for calculation in PerformanceDataCalculation.const.VALUES:
        calculation_obj = PerformanceDataCalculation(
            id=calculation.value,
            name=calculation.name,
            description=calculation.description,
            data_category_id=calculation.category.value,
        )
        db_session.add(calculation_obj)

    print("Adding categories and calculations")
