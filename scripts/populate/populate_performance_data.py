from sqlmodel import Session

from models.performance import PerformanceWindowCalculationCategory, PerformanceWindowCalculationType


def create_performance_data(db_session: Session, ) -> None:
    for item in PerformanceWindowCalculationCategory.const.VALUES:
        category_obj = PerformanceWindowCalculationCategory(
            id=item.value,
            name=item.name,
        )
        db_session.add(category_obj)

    for calculation in PerformanceWindowCalculationType.const.VALUES:
        calculation_obj = PerformanceWindowCalculationType(
            id=calculation.value,
            name=calculation.name,
            description=calculation.description,
            data_category_id=calculation.category.value,
        )
        db_session.add(calculation_obj)

    print("Adding categories and calculations")
