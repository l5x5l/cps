def change_str_to_process_optino(process_option_str:str):
    """
    server의 utils.change_process_option_to_str의 반대버젼
    하나의 str형식으로 이루어져있는 공정설정값들을 원래 형태로 변환시킨다
    """
    process_list = process_option_str.split('/')

    process_list[4] = int(process_list[4])
    process_list[5] = list(map(int,process_list[5].split('-')))
    process_list[6] = list(map(int,process_list[6].split('-')))
    process_list[7] = list(map(int,process_list[7].split('-')))

    return process_list