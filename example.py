from config_editor.config_editor import ConfigEditor

if __name__ == '__main__':
    ConfigEditor(config_dir='example_config/config/',
                 default_config_dir='example_config/default_config/',
                 output_config_dir='example_config/edited_config/').run()
