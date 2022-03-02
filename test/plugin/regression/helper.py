import numpy as np

class DictCheckMixIn:
    ROWFORMAT = "{:>15s} {:>20s} {:>20s}\n"

    @staticmethod
    def check_dict_key_mismatch(obtained: dict, baseline: dict):
        if set(obtained) == set(baseline):
            return set(obtained.keys()), ""
        else:
            matched_keys = set(obtained) & set(baseline)
            error_msg = "The keys in obtained result differ from baseline result.\n"
            error_msg += f"  Matched keys:          {str(list(matched_keys))}\n"
            error_msg += f"  New in obtained:       {str(list(set(obtained) - set(baseline)))}\n"
            error_msg += f"  Missing from obtained: {str(list(set(baseline) - set(obtained)))}\n"
            error_msg += "To update values, use --rebase option.\n\n"
            return matched_keys, error_msg

    def check_dict_data_types(self, obtained: dict, baseline: dict, type_getter=lambda x: (type(x), type(x).__name__)):
        error_msg = ""

        key_set = set()
        for key in set(obtained) & set(baseline):
            obtained_value = obtained[key]
            baseline_value = baseline[key]
            obtained_dtype, obtained_dtype_name = type_getter(obtained_value)
            baseline_dtype, baseline_dtype_name = type_getter(baseline_value)

            if obtained_dtype != baseline_dtype:
                if np.issubdtype(obtained_dtype, np.number) and np.issubdtype(baseline_dtype, np.number):
                    key_set.add(key)
                elif np.issubdtype(obtained_dtype, str) and np.issubdtype(baseline_dtype, str):
                    key_set.add(key)
                else:
                    if error_msg == "":
                        error_msg += "Data types are not the same:\n"
                        error_msg += self.ROWFORMAT.format("Key", "ObtainedType", "BaselineType")
                    error_msg += self.ROWFORMAT.format(str(key), str(obtained_dtype_name), str(baseline_dtype_name))

        if error_msg != "":
            error_msg += "To update values, use --rebase option.\n\n"
        return key_set, error_msg

    def check_dict_data_shapes(self, obtained: dict, baseline: dict, shape_getter=lambda x: x.shape):
        error_msg = ""

        key_set = set()
        for key in set(obtained) & set(baseline):
            obtained_value = obtained[key]
            baseline_value = baseline[key]
            obtained_shape = shape_getter(obtained_value)
            baseline_shape = shape_getter(baseline_value)

            if obtained_shape != baseline_shape:
                if error_msg == "":
                    error_msg += "Data shapes are not the same:\n"
                    error_msg += self.ROWFORMAT.format("Key", "ObtainedShape", "BaselineShape")
                error_msg += self.ROWFORMAT.format(str(key), str(obtained_shape), str(baseline_shape))
            else:
                key_set.add(key)

        if error_msg != "":
            error_msg += "To update values, use --rebase option.\n\n"
        return key_set, error_msg

dict_check = DictCheckMixIn()
