import json
from typing import Union

from aws_lambda_powertools.utilities.data_masking.provider import Provider


class DataMasking:
    def __init__(self, provider=None):
        if provider is None:
            self.provider = Provider()
        else:
            self.provider = provider

    def encrypt(self, data, fields=None, **provider_options):
        return self._apply_action(data, fields, self.provider.encrypt, **provider_options)

    def decrypt(self, data, fields=None, **provider_options):
        return self._apply_action(data, fields, self.provider.decrypt, **provider_options)

    def mask(self, data, fields=None, **provider_options):
        return self._apply_action(data, fields, self.provider.mask, **provider_options)

    def _apply_action(self, data, fields, action, **provider_options):
        if fields is not None:
            return self._apply_action_to_fields(data, fields, action, **provider_options)
        else:
            return action(data, **provider_options)

    def _apply_action_to_fields(self, data: Union[dict, str], fields, action, **provider_options) -> str:
        """
        Apply the specified action to the specified fields in the input data.

        This method is takes the input data, which can be either a dictionary or a JSON string representation
        of a dictionary, and applies a mask, an encryption, or a decryption to the specified fields.

        Parameters:
            data (Union[dict, str]): The input data to process. It can be either a dictionary or a JSON string
                representation of a dictionary.
            fields (list): A list of fields to apply the action to. Each field can be specified as a string or
                a list of strings representing nested keys in the dictionary.
            action (callable): The action to apply to the fields. It should be a callable that takes the current
                value of the field as the first argument and any additional arguments that might be required
                for the action. It performs an operation on the current value using the provided arguments and
                returns the modified value.
            **provider_options: Additional keyword arguments to pass to the 'action' function.

        Returns:
            str: A JSON string representation of the modified dictionary after applying the action to the
            specified fields.

        Raises:
            ValueError: If 'fields' parameter is None.
            TypeError: If the 'data' parameter is not a dictionary or a JSON string representation of a dictionary.
            KeyError: If specified 'fields' do not exist in input data
        """

        if fields is None:
            raise ValueError("No fields specified.")

        if isinstance(data, str):
            # Parse JSON string as dictionary
            my_dict_parsed = json.loads(data)
        elif isinstance(data, dict):
            # Turn into json string so everything has quotes around it
            my_dict_parsed = json.dumps(data)
            # Turn back into dict so can parse it
            my_dict_parsed = json.loads(my_dict_parsed)
        else:
            raise TypeError(
                "Unsupported data type. The 'data' parameter must be a dictionary or a JSON string "
                "representation of a dictionary."
            )

        for field in fields:
            if not isinstance(field, str):
                field = json.dumps(field)
            keys = field.split(".")

            curr_dict = my_dict_parsed
            for key in keys[:-1]:
                curr_dict = curr_dict[key]
            valtochange = curr_dict[(keys[-1])]
            curr_dict[keys[-1]] = action(valtochange, **provider_options)

        return my_dict_parsed