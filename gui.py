# https://www.geeksforgeeks.org/hierarchical-tv-in-python-gui-application/
# https://pythonguides.com/python-tkinter-tv/
# https://pythonguides.com/python-tkinter-treeview/
# https://stackoverflow.com/questions/59594483/tkinter-treeview-expand-all-child-nodes
# https://pythonassets.com/posts/drop-down-list-combobox-in-tk-tkinter/

import tkinter as tk
from tkinter import ttk
import copy
from config_loader import BaseConfigLoader
from dict_reader import DictRecursivelyReader


class GUI:
    def __init__(self, config_dict):

        self.config_dict = config_dict
        self.edited_config_dict = copy.deepcopy(self.config_dict)
        # -------------------------------------------------------------------
        # Constants
        # -------------------------------------------------------------------
        self.values_for_key = ['', 'key']
        self.list_key_prefix = '-LIST-: '
        self.list_value_for_cbb_boolean = [True, False]

        # -------------------------------------------------------------------
        # STATE
        # -------------------------------------------------------------------
        # self.__selected_key = None
        # self.__selected_value = None

        # -------------------------------------------------------------------

        self.app = tk.Tk()
        self.app.title('YAML Editor V.1.0.0')
        self.app.geometry('2000x500')

        self.frm_tv = ttk.Frame(self.app)
        self.frm_tv.pack(side=tk.LEFT, fill=tk.X)

        self.frm_edit = ttk.Frame(self.app)
        self.frm_edit.pack(side=tk.LEFT, fill=tk.BOTH)

        # -------------------------------------------------------------------

        self.tv = ttk.Treeview(self.frm_tv,
                               columns=('Value', 'Type'),
                               height=100,
                               selectmode='browse')
        self.tv.bind('<ButtonRelease-1>', func=self._action_tk_click_edit)

        sb_h = ttk.Scrollbar(self.frm_tv, orient=tk.HORIZONTAL)
        sb_h.config(command=self.tv.xview)

        sb_v = ttk.Scrollbar(self.frm_tv, orient=tk.VERTICAL)
        sb_v.config(command=self.tv.yview)

        self.tv.config(yscrollcommand=sb_v.set,
                       xscrollcommand=sb_h.set)
        self.tv.column('#0', width=500)
        self.tv.column('Value', width=500)
        self.tv.column('Type', anchor=tk.CENTER, width=150)
        self.tv.heading('#0', text='', anchor=tk.CENTER)
        self.tv.heading('Value', text='Value', anchor=tk.CENTER)
        self.tv.heading('Type', text='Type', anchor=tk.CENTER)

        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.tv.pack(side=tk.LEFT, fill=tk.BOTH)
        sb_v.pack(side=tk.LEFT, fill=tk.Y)

        # -------------------------------------------------------------------

        self.__rbt_specify_var = tk.BooleanVar()
        self.__edited_selected_value = tk.StringVar()

        self.lab_select_status = tk.Label(self.frm_edit,
                                          text='SELECTD: ',
                                          anchor=tk.W)

        self.lab_value = tk.Label(self.frm_edit,
                                  text='Value: ',
                                  anchor=tk.W)

        self.rbt_specified_val = tk.Radiobutton(self.frm_edit,
                                                text='Value',
                                                variable=self.__rbt_specify_var,
                                                value=True,
                                                state='disabled',
                                                command=self._action_rbt_specified_val)

        self.rbt_specified_none = tk.Radiobutton(self.frm_edit,
                                                 text='None',
                                                 variable=self.__rbt_specify_var,
                                                 value=False,
                                                 state='disabled',
                                                 command=self._action_rbt_specified_none)
        self.rbt_specified_val.select()

        self.txt_value = tk.Entry(self.frm_edit,
                                  textvariable=self.__edited_selected_value,
                                  state='disabled')

        self.cbb_boolean = ttk.Combobox(self.frm_edit,
                                        values=self.list_value_for_cbb_boolean,
                                        state='disabled')

        self.btn_change_value = tk.Button(self.frm_edit,
                                          text='Change Value',
                                          width=100,
                                          height=2,
                                          state='disabled',
                                          command=self._action_btn_change_value)

        self.btn_clear = tk.Button(self.frm_edit,
                                   text='Clear',
                                   width=100,
                                   height=2,
                                   state='active',
                                   command=self._action_btn_clear)

        self.btn_save = tk.Button(self.frm_edit,
                                  text='Save Config',
                                  width=100,
                                  height=2,
                                  state='active',
                                  command=self._action_btn_save)

        self.btn_reset = tk.Button(self.frm_edit,
                                   text='Reset',
                                   width=100,
                                   height=2,
                                   state='active',
                                   command=self._action_btn_reset)

        self.lab_select_status.pack(side=tk.TOP, fill=tk.X)
        self.lab_value.pack(side=tk.TOP, fill=tk.X)
        self.rbt_specified_val.pack(side=tk.TOP, anchor=tk.W)
        self.rbt_specified_none.pack(side=tk.TOP, anchor=tk.W)
        self.txt_value.pack(side=tk.TOP, fill=tk.X)
        self.cbb_boolean.pack(side=tk.TOP, fill=tk.X)
        self.btn_reset.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_save.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_clear.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_change_value.pack(side=tk.BOTTOM, fill=tk.X)

        # -------------------------------------------------------------------

        self._init_branch()

    def _init_branch(self):
        rr = DictRecursivelyReader()
        self.processed_config_dict = dict()
        for file_name in config_dict:
            self.processed_config_dict[file_name] = rr.read(self.config_dict[file_name])
            self._add_brunch(root_name=file_name,
                             config_list=self.processed_config_dict[file_name])

    def _action_btn_reset(self, *args, **kwargs):
        self.edited_config_dict = copy.deepcopy(self.config_dict)
        self._clear_edit()
        self.tv.delete(*self.tv.get_children())
        self._init_branch()

    def _action_btn_save(self, *args, **kwargs):
        pass

    def _clear_edit(self):
        self.__selected_key = None
        self.lab_select_status.configure(text='SELECTD: ')
        self.rbt_specified_val.configure(state='disabled')
        self.rbt_specified_none.configure(state='disabled')
        self.rbt_specified_val.select()
        self.txt_value.delete(0, tk.END)
        self.txt_value.configure(state='disabled')
        self.cbb_boolean.set('')
        self.cbb_boolean.configure(state='disabled')
        self.btn_change_value.configure(state='disabled')

    def _action_rbt_specified_val(self):
        self.txt_value.configure(state='normal')

    def _action_rbt_specified_none(self):
        self.txt_value.configure(state='disabled')

    def _action_btn_change_value(self, *args, **kwargs):
        selected_key = self.tv.focus()
        selected_keys = self._extract_tv_key(selected_key)
        selected_value = self._get_actual_value(selected_keys)

        if isinstance(selected_value, bool):
            index = self.cbb_boolean.current()
            edited_value = self.list_value_for_cbb_boolean[index]
        else:
            if self.__rbt_specify_var.get():
                edited_value = self.__edited_selected_value.get()
                if isinstance(selected_value, int):
                    edited_value = int(edited_value)
                elif isinstance(selected_value, float):
                    edited_value = float(edited_value)
            else:
                edited_value = None
        selected_key = self.tv.focus()

        print('To be value:', edited_value, type(edited_value))
        print('TV before:', self.tv.set(selected_key))
        print('Actual before', selected_value, type(selected_value))

        self.tv.set(selected_key, column='Value', value=str(edited_value))
        self._set_actual_value(keys=selected_keys, set_value=edited_value)

        print('TV after:', self.tv.set(selected_key))
        print('Actual after', self._get_actual_value(selected_keys), type(self._get_actual_value(selected_keys)))

    def _action_btn_clear(self, *args, **kwargs):
        self._clear_edit()
        for i in self.tv.selection():
            self.tv.selection_remove(i)

    def _action_tk_click_edit(self, *args, **kwargs):
        selected_key = self.tv.focus()
        record = self.tv.item(selected_key)

        if len(record['values']) == 0:
            self._clear_edit()
        elif record['values'] == self.values_for_key:
            self._clear_edit()
        else:
            selected_keys = self._extract_tv_key(selected_key)
            selected_value = self._get_actual_value(selected_keys)

            self.lab_select_status.configure(text=f'''SELECTD: {' / '.join(selected_keys)}''')
            self.txt_value.delete(0, tk.END)

            self.btn_change_value.configure(state='normal')
            if isinstance(selected_value, bool):
                self.rbt_specified_val.configure(state='disabled')
                self.rbt_specified_none.configure(state='disabled')
                self.rbt_specified_val.select()
                self.txt_value.configure(state='disabled')
                self.cbb_boolean.configure(state='readonly')
                self.cbb_boolean.set(str(selected_value))
            elif selected_value is None:
                self.rbt_specified_val.configure(state='normal')
                self.rbt_specified_none.configure(state='normal')
                self.rbt_specified_none.select()
                self.txt_value.configure(state='disabled')
                self.cbb_boolean.configure(state='disabled')
                self.cbb_boolean.set('')
            else:
                self.rbt_specified_val.configure(state='normal')
                self.rbt_specified_none.configure(state='normal')
                self.rbt_specified_val.select()
                self.txt_value.configure(state='normal')
                self.cbb_boolean.configure(state='disabled')
                self.txt_value.insert(index=0,
                                      string=str(selected_value))
                self.cbb_boolean.set('')

    def _get_actual_value(self, keys):
        value = None
        for key in keys:
            if str(key).startswith(self.list_key_prefix):
                key = int(key.split(self.list_key_prefix)[-1])
            if value is None:
                value = self.edited_config_dict[key]
            else:
                value = value[key]
        return value

    def _set_actual_value(self, keys, set_value):
        data = None
        for key in keys[:-1]:
            if str(key).startswith(self.list_key_prefix):
                key = int(key.split(self.list_key_prefix)[-1])
            if data is None:
                data = self.edited_config_dict[key]
            else:
                data = data[key]
        data[keys[-1]] = set_value

    def _extract_tv_key(self, key):
        return key.split('__')

    def _add_brunch(self, root_name: str, config_list: list):

        self.tv.insert(parent='',
                       index='end',
                       iid=root_name,
                       text=root_name,
                       values=self.values_for_key,
                       open=False)

        branchs = list()
        created_iids = [root_name]
        for record in config_list:
            branch = [root_name] + record[0] + [record[1]]
            if branch not in branchs:
                branchs.append(branch)
                for i in range(len(branch)):
                    parent = '__'.join(branch[:i])
                    iid = '__'.join(branch[: i + 1])
                    text = branch[: i + 1][-1]
                    if iid not in created_iids:
                        created_iids.append(iid)
                        if i == (len(branch) - 1):
                            values = (record[2], record[3])
                        else:
                            values = self.values_for_key
                        self.tv.insert(parent=parent,
                                       index='end',
                                       iid=iid,
                                       text=text,
                                       values=values,
                                       open=True)

    def run(self):
        self.app.mainloop()


if __name__ == '__main__':
    config_dict = BaseConfigLoader(config_dir='config/').load()
    GUI(config_dict=config_dict).run()
