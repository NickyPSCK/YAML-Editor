import copy
from typing import Optional, List
import tkinter as tk
from tkinter import ttk, messagebox
import yaml
from util.config_loader import BaseConfigLoader, ConfigMelter


class ConfigEditor(tk.Tk):
    def __init__(self,
                 config_dir: str,
                 config_file_names: Optional[List[str]] = None,
                 output_config_dir: Optional[str] = None,
                 default_config_dir: Optional[str] = None):

        super().__init__()

        # ---------------------------------------------------------------------------------------------------
        # Constants and Preset
        # ---------------------------------------------------------------------------------------------------
        self.key_seperator = '/'
        self.values_for_key = ['', 'key']
        self.list_key_prefix = '-LIST-: '
        self.list_value_for_cbb_boolean = [True, False]
        self.font = 'Calibri'
        self.font_size = 12

        # ---------------------------------------------------------------------------------------------------
        # Initial Class Attributes
        # ---------------------------------------------------------------------------------------------------
        self._config_dir = config_dir
        self._config_file_names = config_file_names
        self._output_config_dir = output_config_dir
        self._default_config_dir = default_config_dir

        # ---------------------------------------------------------------------------------------------------
        # Read all config files
        # ---------------------------------------------------------------------------------------------------
        self.config_dict = BaseConfigLoader(config_dir=self._config_dir,
                                            config_file_names=self._config_file_names).load()

        if self._output_config_dir is None:
            self._output_config_dir = config_dir
        else:
            self._output_config_dir = output_config_dir

        if self._default_config_dir is not None:
            self.default_config_dict = BaseConfigLoader(config_dir=self._default_config_dir,
                                                        config_file_names=self._config_file_names).load()
        else:
            self.default_config_dict = None

        self.edited_config_dict = copy.deepcopy(self.config_dict)

        # ---------------------------------------------------------------------------------------------------
        # Create GUI
        # ---------------------------------------------------------------------------------------------------
        self._set_style()
        self._create_gui_master()
        self._create_gui_frames()
        self._create_gui_inside_frame_tv()
        self._create_gui_inside_frame_edit()
        self._init_branch()

    def _set_style(self):
        self.style = ttk.Style()
        self.style.configure('big.TButton', font=(self.font, self.font_size + 1))
        self.style.configure('big.TRadiobutton', font=(self.font, self.font_size))
        self.style.configure('bigbold.TLabel', font=(self.font, self.font_size + 1, 'bold'))
        self.style.configure('big.TLabel', font=(self.font, self.font_size - 1))
        self.style.configure("big.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        self.style.configure("big.Treeview.Heading", font=(self.font, self.font_size, 'bold'))
        self.ccb_font = (self.font, self.font_size - 1)
        self.entry_font = (self.font, self.font_size - 1)
        # self.style.configure('big.TEntry', font=(self.font, self.font_size))
        # self.style.configure('big.TCombobox', font=(self.font, self.font_size + 9))

    def _create_gui_master(self):
        # https://icon-icons.com/icon/YAML-Alt4/131861
        self.iconbitmap(default='./img/yaml_icon.ico')
        self.title('YAML Configuration Editor V.1.0.0')
        self.protocol('WM_DELETE_WINDOW', self.__close_window)
        self.geometry('1450x900+20+20')
        self.minsize(1400, 650)
        # self.maxsize(1800, 5000)
        self.maxsize(None, None)
        # self.resizable(0, 0)

    def _create_gui_frames(self):
        self.frm_tv = ttk.Frame(self)
        self.frm_tv.pack(side=tk.LEFT,
                         fill=tk.X)

        self.frm_edit = ttk.Frame(self)
        self.frm_edit.pack(side=tk.LEFT,
                           fill=tk.BOTH,
                           padx=20,
                           pady=20)

    def _create_gui_inside_frame_tv(self):
        self.tv = ttk.Treeview(self.frm_tv,
                               columns=('Value', 'Type'),
                               height=100,
                               selectmode='browse',
                               style='big.Treeview')

        self.tv.bind('<ButtonRelease-1>', func=self._action_tk_click_edit)

        sb_h = ttk.Scrollbar(self.frm_tv, orient=tk.HORIZONTAL)
        sb_h.config(command=self.tv.xview)

        sb_v = ttk.Scrollbar(self.frm_tv, orient=tk.VERTICAL)
        sb_v.config(command=self.tv.yview)

        self.tv.config(yscrollcommand=sb_v.set,
                       xscrollcommand=sb_h.set)
        self.tv.column('#0', width=400)
        self.tv.column('Value', width=500)
        self.tv.column('Type', anchor=tk.CENTER, width=120)
        self.tv.heading('#0', text='', anchor=tk.CENTER)
        self.tv.heading('Value', text='Value', anchor=tk.CENTER)
        self.tv.heading('Type', text='Type', anchor=tk.CENTER)

        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.tv.pack(side=tk.LEFT, fill=tk.BOTH)
        sb_v.pack(side=tk.LEFT, fill=tk.Y)

    def _create_gui_inside_frame_edit(self):
        self.__rbt_dtype = tk.StringVar()
        self.entry_value_str_var = tk.StringVar()
        self.entry_select_status_str_var = tk.StringVar()

        self.lab_key = ttk.Label(self.frm_edit,
                                 text='Key: ',
                                 anchor=tk.W,
                                 style='bigbold.TLabel')

        self.entry_select_status = ttk.Entry(self.frm_edit,
                                             text='',
                                             textvariable=self.entry_select_status_str_var,
                                             state='readonly',
                                             # style='big.TEntry',
                                             font=self.entry_font)

        self.frm_rbt_dtype = ttk.Frame(self.frm_edit)

        self.lab_value_type = ttk.Label(self.frm_rbt_dtype,
                                        text='Type: ',
                                        anchor=tk.W,
                                        style='bigbold.TLabel')

        self.rbt_dtype_str = ttk.Radiobutton(self.frm_rbt_dtype,
                                             command=self._action_rbt_dtype_str_int_float,
                                             text='string',
                                             variable=self.__rbt_dtype,
                                             value='str',
                                             state='disabled',
                                             style='big.TRadiobutton')

        self.rbt_dtype_int = ttk.Radiobutton(self.frm_rbt_dtype,
                                             command=self._action_rbt_dtype_str_int_float,
                                             text='integer',
                                             variable=self.__rbt_dtype,
                                             value='integer',
                                             state='disabled',
                                             style='big.TRadiobutton')

        self.rbt_dtype_float = ttk.Radiobutton(self.frm_rbt_dtype,
                                               command=self._action_rbt_dtype_str_int_float,
                                               text='float',
                                               variable=self.__rbt_dtype,
                                               value='float',
                                               state='disabled',
                                               style='big.TRadiobutton')

        self.rbt_dtype_bool = ttk.Radiobutton(self.frm_rbt_dtype,
                                              command=self._action_rbt_dtype_bool,
                                              text='bool',
                                              variable=self.__rbt_dtype,
                                              value='bool',
                                              state='disabled',
                                              style='big.TRadiobutton')

        self.rbt_dtype_none = ttk.Radiobutton(self.frm_rbt_dtype,
                                              command=self._action_rbt_dtype_none,
                                              text='none',
                                              variable=self.__rbt_dtype,
                                              value='none',
                                              state='disabled',
                                              style='big.TRadiobutton')

        self.lab_value = ttk.Label(self.frm_edit,
                                   text='Value: ',
                                   anchor=tk.W,
                                   style='bigbold.TLabel')

        self.entry_value = ttk.Entry(self.frm_edit,
                                     textvariable=self.entry_value_str_var,
                                     state='disabled',
                                     # style='big.TEntry',
                                     font=self.entry_font)

        self.cbb_boolean = ttk.Combobox(self.frm_edit,
                                        values=self.list_value_for_cbb_boolean,
                                        state='disabled',
                                        # style='big.TCombobox',
                                        font=self.ccb_font)

        self.lab_warning = ttk.Label(self.frm_edit,
                                     text='',
                                     foreground='#f00',
                                     anchor=tk.CENTER,
                                     style='bigbold.TLabel')

        self.frm_btn_change_clear = ttk.Frame(self.frm_edit)

        self.btn_change_value = ttk.Button(self.frm_btn_change_clear,
                                           command=self._action_btn_change_value,
                                           text='\nChange Value\n',
                                           takefocus=False,
                                           state='disabled',
                                           style='big.TButton')
        self.btn_change_value['width'] = 25

        self.btn_clear = ttk.Button(self.frm_btn_change_clear,
                                    command=self._action_btn_clear,
                                    text='\nClear\n',
                                    takefocus=False,
                                    state='normal',
                                    style='big.TButton')
        self.btn_clear['width'] = 25

        self.btn_delete_key = ttk.Button(self.frm_edit,
                                         command=self._action_btn_delete,
                                         text='Delete',
                                         takefocus=False,
                                         state='disabled',
                                         style='big.TButton')
        self.btn_delete_key['width'] = 120

        self.frm_dir_status = ttk.Frame(self.frm_edit)

        self.lab_topic_dir = ttk.Label(self.frm_dir_status,
                                       text='Directory: ',
                                       anchor=tk.W,
                                       style='bigbold.TLabel')

        self.lab_config_dir = ttk.Label(self.frm_dir_status,
                                        text=f'- Config: {self._config_dir}',
                                        anchor=tk.W,
                                        style='big.TLabel')

        self.lab_default_config_dir = ttk.Label(self.frm_dir_status,
                                                text=f'- Default Config: {self._default_config_dir}',
                                                anchor=tk.W,
                                                style='big.TLabel')

        self.lab_output_config_dir = ttk.Label(self.frm_dir_status,
                                               text=f'- Output Config: {self._output_config_dir}',
                                               anchor=tk.W,
                                               style='big.TLabel')

        self.frm_btn_undo_reset = ttk.Frame(self.frm_edit)

        self.btn_undo_all = ttk.Button(self.frm_btn_undo_reset,
                                       command=self._action_btn_undo_all,
                                       text='Undo All',
                                       takefocus=False,
                                       state='disabled',
                                       style='big.TButton')
        self.btn_undo_all['width'] = 25

        self.btn_reset = ttk.Button(self.frm_btn_undo_reset,
                                    command=self._action_btn_reset,
                                    text='Load Default',
                                    takefocus=False,
                                    state='normal',
                                    style='big.TButton')
        self.btn_reset['width'] = 25

        self.btn_save = ttk.Button(self.frm_edit,
                                   command=self._action_btn_save,
                                   text='\nSave Config\n',
                                   takefocus=False,
                                   state='normal',
                                   style='big.TButton')
        self.btn_save['width'] = 1000

        self.lab_key.pack(side=tk.TOP, fill=tk.X)
        self.entry_select_status.pack(side=tk.TOP, fill=tk.X)

        self.frm_rbt_dtype.pack(side=tk.TOP, fill=tk.X, pady=20)
        self.lab_value_type.pack(side=tk.TOP, anchor=tk.W)
        self.rbt_dtype_str.pack(side=tk.LEFT, anchor=tk.W, padx=7)
        self.rbt_dtype_int.pack(side=tk.LEFT, anchor=tk.W, padx=7)
        self.rbt_dtype_float.pack(side=tk.LEFT, anchor=tk.W, padx=7)
        self.rbt_dtype_bool.pack(side=tk.LEFT, anchor=tk.W, padx=7)
        self.rbt_dtype_none.pack(side=tk.LEFT, anchor=tk.W, padx=7)

        self.lab_value.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)
        self.entry_value.pack(side=tk.TOP, fill=tk.X)
        self.cbb_boolean.pack(side=tk.TOP, fill=tk.X)
        self.lab_warning.pack(side=tk.TOP, fill=tk.X)

        self.frm_btn_change_clear.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.btn_change_value.pack(side=tk.LEFT)
        self.btn_clear.pack(side=tk.RIGHT)

        self.btn_save.pack(side=tk.BOTTOM, fill=tk.X)

        self.frm_btn_undo_reset.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.btn_undo_all.pack(side=tk.LEFT)
        self.btn_reset.pack(side=tk.RIGHT)

        self.frm_dir_status.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        self.lab_topic_dir.pack(side=tk.TOP, anchor=tk.W)
        self.lab_config_dir.pack(side=tk.TOP, anchor=tk.W)
        self.lab_default_config_dir.pack(side=tk.TOP, anchor=tk.W)
        self.lab_output_config_dir.pack(side=tk.TOP, anchor=tk.W)

        # self.btn_delete_key.pack(side=tk.BOTTOM)

        self._clear_edit()

    def _add_brunch(self,
                    root_name: str,
                    config_list: list):

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
                            values = (record[2], type(record[2]))
                        else:
                            values = self.values_for_key
                        self.tv.insert(parent=parent,
                                       index='end',
                                       iid=iid,
                                       text=text,
                                       values=values,
                                       open=True)

    def _init_branch(self):
        cm = ConfigMelter()
        processed_config_dict = dict()
        for file_name in self.edited_config_dict:
            processed_config_dict[file_name] = cm.melt(self.edited_config_dict[file_name])
            self._add_brunch(root_name=file_name,
                             config_list=processed_config_dict[file_name])

    def _get_actual_value(self, keys):
        if len(keys) == 1:
            return self.edited_config_dict[keys[0]]
        else:
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
        if len(keys) == 1:
            self.edited_config_dict[keys[0]] = set_value
        else:
            data = None
            for key in keys[:-1]:
                if str(key).startswith(self.list_key_prefix):
                    key = int(key.split(self.list_key_prefix)[-1])
                if data is None:
                    data = self.edited_config_dict[key]
                else:
                    data = data[key]
            if str(keys[-1]).startswith(self.list_key_prefix):
                key = int(keys[-1].split(self.list_key_prefix)[-1])
                data[key] = set_value
            else:
                data[keys[-1]] = set_value

    def _del_actual_value(self, keys):
        if len(keys) == 1:
            del self.edited_config_dict[keys[0]]
        else:
            data = None
            for key in keys[:-1]:
                if str(key).startswith(self.list_key_prefix):
                    key = int(key.split(self.list_key_prefix)[-1])
                if data is None:
                    data = self.edited_config_dict[key]
                else:
                    data = data[key]

            if str(keys[-1]).startswith(self.list_key_prefix):
                key = int(keys[-1].split(self.list_key_prefix)[-1])
                del data[key]
            else:
                del data[keys[-1]]

    def _extract_tv_key(self, key):
        return key.split('__')

    def _clear_edit(self, reset_save_btn=True):
        self.entry_select_status_str_var.set('')
        self.lab_warning.configure(text='')
        self.rbt_dtype_str.configure(state='disabled')
        self.rbt_dtype_int.configure(state='disabled')
        self.rbt_dtype_float.configure(state='disabled')
        self.rbt_dtype_bool.configure(state='disabled')
        self.rbt_dtype_none.configure(state='disabled')
        self.rbt_dtype_str.invoke()
        self.entry_value_str_var.set('')
        self.entry_value.configure(state='disabled')
        self.cbb_boolean.set('')
        self.cbb_boolean.configure(state='disabled')
        self.btn_change_value.configure(state='disabled')
        self.btn_delete_key.configure(state='disabled')
        if reset_save_btn:
            self.btn_save.configure(state='disabled')
        if self.default_config_dict is None:
            self.btn_reset.configure(state='disabled')

    def _action_tk_click_edit(self, *args, **kwargs):
        selected_key = self.tv.focus()
        record = self.tv.item(selected_key)
        if len(record['values']) == 0:
            self._clear_edit(reset_save_btn=False)
        elif record['values'] == self.values_for_key:
            self._clear_edit(reset_save_btn=False)
            self.btn_delete_key.configure(state='normal')
        else:
            selected_keys = self._extract_tv_key(selected_key)
            selected_value = self._get_actual_value(selected_keys)
            self.entry_select_status_str_var.set(f'''{self.key_seperator.join(selected_keys)}''')
            self.entry_value_str_var.set('')
            self.lab_warning.configure(text='')
            self.btn_change_value.configure(state='normal')
            self.btn_delete_key.configure(state='normal')

            self.rbt_dtype_str.configure(state='normal')
            self.rbt_dtype_int.configure(state='normal')
            self.rbt_dtype_float.configure(state='normal')
            self.rbt_dtype_bool.configure(state='normal')
            self.rbt_dtype_none.configure(state='normal')

            if isinstance(selected_value, bool):
                self.rbt_dtype_bool.invoke()
                self.entry_value.configure(state='disabled')
                self.cbb_boolean.configure(state='readonly')
                self.cbb_boolean.set(str(selected_value))
            elif isinstance(selected_value, int):
                self.rbt_dtype_int.invoke()
                self.entry_value.configure(state='normal')
                self.cbb_boolean.configure(state='disabled')
                self.entry_value_str_var.set(str(selected_value))
                self.cbb_boolean.set('')
            elif isinstance(selected_value, float):
                self.rbt_dtype_float.invoke()
                self.entry_value.configure(state='normal')
                self.cbb_boolean.configure(state='disabled')
                self.entry_value_str_var.set(str(selected_value))
                self.cbb_boolean.set('')
            elif selected_value is None:
                self.rbt_dtype_none.invoke()
                self.entry_value.configure(state='disabled')
                self.cbb_boolean.configure(state='disabled')
                self.cbb_boolean.set('')
            else:  # isinstance(selected_value, str):
                self.rbt_dtype_str.invoke()
                self.entry_value.configure(state='normal')
                self.cbb_boolean.configure(state='disabled')
                self.entry_value_str_var.set(str(selected_value))
                self.cbb_boolean.set('')

    def _make_sure_msg_box(message):
        def _make_sure(class_method):
            def method_wrapper(self, *arg, **kwarg):
                if messagebox.askokcancel(title='Warning', message=message):
                    return class_method(self, *arg, **kwarg)
                else:
                    pass
            return method_wrapper
        return _make_sure

    def _action_btn_clear(self, *args, **kwargs):
        self._clear_edit(reset_save_btn=False)
        for i in self.tv.selection():
            self.tv.selection_remove(i)

    @_make_sure_msg_box(message='Do you want to change the value?')
    def _action_btn_change_value(self, *args, **kwargs):
        selected_key = self.tv.focus()
        selected_keys = self._extract_tv_key(selected_key)
        # selected_value = self._get_actual_value(selected_keys)

        input_type_str = self.__rbt_dtype.get()
        if input_type_str == 'bool':
            index = self.cbb_boolean.current()
            edited_value = self.list_value_for_cbb_boolean[index]
            is_error = False
        elif input_type_str == 'none':
            edited_value = None
            is_error = False
        else:
            edited_value = self.entry_value_str_var.get()
            if input_type_str == 'integer':
                try:
                    edited_value = int(edited_value)
                    self.lab_warning.configure(text='')
                    is_error = False
                except ValueError:
                    self.lab_warning.configure(text='Value must be integer number.')
                    is_error = True
            elif input_type_str == 'float':
                try:
                    edited_value = float(edited_value)
                    self.lab_warning.configure(text='')
                    is_error = False
                except ValueError:
                    self.lab_warning.configure(text='Value must be floating point number.')
                    is_error = True
            else:
                self.lab_warning.configure(text='')
                is_error = False

        if not is_error:
            # print('To be value:', edited_value, type(edited_value))
            # print('TV before:', self.tv.set(selected_key))
            # print('Actual before', selected_value, type(selected_value))
            self.tv.set(selected_key, column='Value', value=str(edited_value))
            self.tv.set(selected_key, column='Type', value=type(edited_value))
            self._set_actual_value(keys=selected_keys, set_value=edited_value)
            self.btn_undo_all.configure(state='normal')
            self.btn_save.configure(state='normal')
            # print('TV after:', self.tv.set(selected_key))
            # print('Actual after', self._get_actual_value(selected_keys), type(self._get_actual_value(selected_keys)))

    @_make_sure_msg_box(message='Do you want to undo all changed?')
    def _action_btn_undo_all(self, *args, **kwargs):
        self.edited_config_dict = copy.deepcopy(self.config_dict)
        self._clear_edit()
        self.tv.delete(*self.tv.get_children())
        self._init_branch()
        self.btn_undo_all.configure(state='disabled')

    @_make_sure_msg_box(message='Do you want to reset to default config?')
    def _action_btn_reset(self, *args, **kwargs):
        self.edited_config_dict = copy.deepcopy(self.default_config_dict)
        self._clear_edit()
        self.tv.delete(*self.tv.get_children())
        self._init_branch()
        self.btn_undo_all.configure(state='normal')
        self.btn_save.configure(state='normal')

    @_make_sure_msg_box(message='Do you want to save config to config files?')
    def _action_btn_save(self, *args, **kwargs):
        for file_name in self.edited_config_dict:
            with open(f'{self._output_config_dir}{file_name}.yaml', 'w') as f:
                yaml.dump(self.edited_config_dict[file_name], f, sort_keys=False)
        self.btn_undo_all.configure(state='disabled')
        self.btn_save.configure(state='disabled')

    @_make_sure_msg_box(message='Do you want to delete?')
    def _action_btn_delete(self, *args, **kwargs):
        selected_key = self.tv.focus()
        selected_keys = self._extract_tv_key(selected_key)
        self.tv.delete(selected_key)
        self._del_actual_value(keys=selected_keys)

        selected_key = self.tv.focus()
        record = self.tv.item(selected_key)
        if len(record['values']) == 0:
            self.btn_delete_key.configure(state='disabled')

    def _action_rbt_dtype_str_int_float(self):
        self.entry_value.configure(state='normal')
        self.cbb_boolean.configure(state='disabled')

    def _action_rbt_dtype_bool(self):
        self.entry_value.configure(state='disabled')
        self.cbb_boolean.configure(state='readonly')
        selected_key = self.tv.focus()
        selected_keys = self._extract_tv_key(selected_key)
        selected_value = self._get_actual_value(selected_keys)
        if isinstance(selected_value, bool):
            self.cbb_boolean.set(str(selected_value))
        else:
            self.cbb_boolean.set(str(True))

    def _action_rbt_dtype_none(self):
        self.entry_value.configure(state='disabled')
        self.cbb_boolean.configure(state='disabled')

    def run(self):
        self.mainloop()

    def __close_window(self):
        btn_save_state = self.btn_save.state()
        if len(btn_save_state) == 0:
            save = False
        elif btn_save_state[0] == 'active':
            save = False
        elif btn_save_state[0] == 'disabled':
            save = True
        else:
            save = True

        if save:
            self.destroy()
        else:
            if messagebox.askokcancel(title='Warning',
                                      message='Do you want to close this program without saving?'):
                self.destroy()
            else:
                self.btn_save.configure(state='active')
