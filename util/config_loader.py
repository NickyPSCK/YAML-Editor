import os
import copy
from collections import OrderedDict
from collections.abc import Mapping
from typing import Optional, Literal, List
from glob import glob

import yaml
from yaml.loader import SafeLoader


class BaseConfigLoader:
    '''BaseConfigLoader

    :param config_dir: Directory that contains configuration file(s).
    :type config_dir: str

    :param config_file_names: List of configuration file(s) to be read.
                              If None, read all configuration files.
    :type config_file_names: list, optional, defaults to None

    '''
    def __init__(self,
                 config_dir: str,
                 config_file_names: Optional[List[str]] = None):
        self.config_dir = config_dir
        self.config_file_names = self._init_config_file_names(config_dir=config_dir,
                                                              config_file_names=config_file_names)

    @staticmethod
    def deep_update(source: dict,
                    overrides: dict) -> dict:
        '''Update a nested dictionary or similar mapping.

        :param source: Dictionary to be updated.
        :type source: dict

        :param overrides: Dictionary which contains updated values.
        :type overrides: dict

        .. seealso::
        https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
        '''

        for key, value in overrides.items():
            if isinstance(value, Mapping) and value:
                returned = ConfigLoader.deep_update(source.get(key, {}),
                                                    value)
                source[key] = returned
            else:
                source[key] = overrides[key]
        return source

    def _init_config_file_names(self,
                                config_dir: str,
                                config_file_names: list) -> list:
        if config_file_names is None:
            config_file_names = list()
            config_path_list = glob(config_dir + '*.yaml')
            for config_path in config_path_list:
                config_file_names.append(config_path.split(os.sep)[-1])
        return config_file_names

    def _read_config(self,
                     file_path: str) -> dict:
        with open(file_path) as f:
            config_dict = yaml.load(f, Loader=SafeLoader)

        return config_dict

    def _load(self) -> dict:
        '''Returns loaded configuration dictionary

        :rtype: dict
        :return: Configuration dictionary

        '''
        config_dicts = dict()
        for config_file_name in self.config_file_names:
            self.config_file_path = os.path.join(self.config_dir,
                                                 config_file_name)
            config_dict = self._read_config(self.config_file_path)
            config_dicts[config_file_name.split('.')[0]] = config_dict
        return config_dicts

    def load(self) -> dict:
        '''Returns loaded configuration dictionary

        :rtype: dict
        :return: Configuration dictionary

        '''
        return self._load()


class ConfigMelter:
    '''ConfigMelter
    '''
    def __init__(self):
        self.list_key_prefix = '-LIST-: '
        self.__result = list()

    def melt(self,
             data_dict) -> List[list]:
        '''Returns unnested structure of input data_dict

        :param data_dict: dictionary to be unnested.
        :type data_dict: dict

        :rtype: dict
        :return: Unnested structure of input data_dict

        '''
        data_dict = copy.deepcopy(data_dict)
        self.__result = list()
        self._recursively_melt(data_dict)
        return self.__result

    def _recursively_melt(self,
                          data,
                          state=None):
        if state is None:
            state = list()
        else:
            state = state

        for key in data:
            if isinstance(data[key], dict) or isinstance(data[key], list):
                state.append(key)

                if isinstance(data[key], list):
                    converted_list = OrderedDict()
                    for i in range(len(data[key])):
                        k = f'{self.list_key_prefix}{i}'
                        converted_list[k] = copy.deepcopy(data[key][i])
                    data[key] = copy.deepcopy(converted_list)

                self._recursively_melt(data[key],
                                       state=state)
                state.pop()
            else:
                self.__result.append([state.copy(),
                                      key,
                                      data[key]])

                # space = len(state) * '  '
                # print(f'{space}{key}: {data[key]}, {state}')


class ConfigLoader(BaseConfigLoader):
    '''ConfigLoader

    :param config_dir: Directory that contains configuration file(s).
    :type config_dir: str

    :param running_env: Running environment.
    :type running_env: Literal['DEV', 'NON_PROD', 'PROD'], optional, defaults to 'DEV'

    :param config_file_names: List of configuration file(s) to be read.
                              If None, read all configuration files.
    :type config_file_names: list, optional, defaults to None

    '''
    def __init__(self,
                 config_dir: str,
                 running_env: Optional[Literal['DEV', 'NON_PROD', 'PROD']] = 'DEV',
                 config_file_names: Optional[List[str]] = None):

        super().__init__(config_dir=config_dir,
                         config_file_names=config_file_names)
        self.running_env = running_env.upper()

    def __merge_indep_and_dep(self,
                              config_dict: dict) -> dict:
        processed_config_dict = dict()
        indep_config_dict = config_dict.get('INDEP_ENV', dict())
        dep_config_dict = config_dict.get('DEP_ENV', dict()).get(self.running_env, dict())
        processed_config_dict = self.deep_update(processed_config_dict, indep_config_dict)
        processed_config_dict = self.deep_update(processed_config_dict, dep_config_dict)
        return processed_config_dict

    def _load(self) -> dict:
        '''Returns loaded configuration dictionary

        :rtype: dict
        :return: Configuration dictionary

        '''
        all_processed_config_dicts = dict()
        for config_file_name in self.config_file_names:
            self.config_file_path = os.path.join(self.config_dir, config_file_name)
            config_dict = self._read_config(self.config_file_path)
            config_dict = self.__merge_indep_and_dep(config_dict)
            all_processed_config_dicts = self.deep_update(all_processed_config_dicts, config_dict)
        return all_processed_config_dicts


if __name__ == '__main__':
    # cl = BaseConfigLoader(config_dir='./config/')
    # CONFIG = cl.load()
    # print(CONFIG)

    cl = ConfigLoader(config_dir='./config/',
                      running_env='DEV')

    CONFIG = cl.load()
    print(CONFIG)
