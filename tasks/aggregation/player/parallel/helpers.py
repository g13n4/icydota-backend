from typing import Literal


class PlayerParallelKeyCreator:
    def __init__(
            self,
            processing_type: Literal["aggregation", "cross-comparison"],
            PoT: Literal["player", "team"],
            aggregation_type: int,
            league_id: int | None = None,
            patch_id: int | None = None,
            ):
        self._base = f"{processing_type}-{PoT}-{aggregation_type}-{league_id}-{patch_id}"


    @property
    def base(self) -> str:
        return self._base


    @property
    def keys(self) -> str:
        return self._base + "-keys"


    @property
    def AGC(self) -> str:
        return self._base + "-AGC"
