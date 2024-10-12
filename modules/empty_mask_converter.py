class EmptyMaskConverter:
    NONE_VALUE = 0

    @staticmethod
    def mask_value_converter(value: int) -> int | None:
        return None if value == EmptyMaskConverter.NONE_VALUE else value

    @staticmethod
    def convert_to_mask(empty_fields: list[int]) -> int:
        """Turn a list of integers into a mask"""
        return int("".join(map(str, empty_fields)), 2)

    @staticmethod
    def convert_from_mask(numeric_mask: int, length: int) -> list[int]:
        """Turn a small integer into a list of integers:
        first: turn it into a binary number and then into a list
        second: remove 'b' - binary and '0' - signed/unsigned bit
        third: turn it into integers and get a slice from the beginning to the number of fields (length)
        """
        coded_values = list(map(int, list(bin(numeric_mask))[2:]))[:length]
        return ([0] * (length - len(coded_values))) + coded_values

    @staticmethod
    def convert_from_mask_to_dict(
        numeric_mask: int, keys: list[int | str]
    ) -> dict[int | str, int | None]:
        """Turn a small integer into a dictionary"""

        mask_values = EmptyMaskConverter.convert_from_mask(numeric_mask, len(keys))
        return {
            key: EmptyMaskConverter.mask_value_converter(value)
            for key, value in zip(keys, mask_values)
        }
