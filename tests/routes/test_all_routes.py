from tests.routes.test_aggregation_route import AggregationRouteTest
from tests.routes.test_ccomparison_route import CrossComparisonRouteTest
from tests.routes.test_match_route import MatchRouteTest


class AllRoutesTest(MatchRouteTest, AggregationRouteTest, CrossComparisonRouteTest):
    """
    Test all routes
    """
