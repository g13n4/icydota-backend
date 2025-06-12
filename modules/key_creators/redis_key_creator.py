from typing import Literal


class RedisParallelKeyCreator:
    def __init__(
            self,
            processing_type: Literal["aggregation", "cross-comparison"],
            PoT: Literal["player", "team"],
            aggregation_type: int | None = None,
            league_id: int | None = None,
            patch_id: int | None = None,
            **kwargs
            ):
        postfix = ""
        if (ccomp_pos_id := kwargs.get("ccomp_pos_id", None)):
            postfix = f"-{ccomp_pos_id}"

        self._base = f"{processing_type}-{PoT}-{aggregation_type}-{league_id}-{patch_id}{postfix}"


    @property
    def base(self) -> str:
        return self._base


    @property
    def keys(self) -> str:
        return self._base + "-keys"


    @property
    def AGC(self) -> str:
        return self._base + "-AGC"
