import copy
from collections import OrderedDict


class DictRecursivelyReader:
    def __init__(self,
                 verbose: bool = False):
        self.verbose = verbose
        self.list_key_prefix = '-LIST-: '
        self.__result = list()

    def read(self,
             data_dict):
        data_dict = copy.deepcopy(data_dict)
        self.__result = list()
        self._recursively_read(data_dict)
        return self.__result

    def _recursively_read(self,
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

                self._recursively_read(data[key],
                                       state=state)
                state.pop()
            else:
                self.__result.append([state.copy(),
                                      key,
                                      data[key],
                                      type(data[key])])
                if self.verbose:
                    space = len(state) * '  '
                    print(f'{space}{key}: {data[key]}, {state}')


if __name__ == '__main__':
    data = {'a': 1,
            'b': {'x': 1,
                  'y': {'i': 1,
                        'j': {'m': 1,
                              'n': {'m': 1,
                                    'n': 2}}},
                  'z': {'m': 1,
                        'n': 2}}}
    print(DictRecursivelyReader().read(data))
