import os
import extract_IO
import re
import regex_patterns
pat_inst_sv = r'\s(\w+)\s+#\s*[(]\s*[.]\s*[\w*]+\s*[(]\s*[\w*]+\s*[)]'
pat_inst_v = r'\s(\w+)\s+\w+\s*[(]\s*[.]\s*[\w*]+\s*[(]\s*[\w*]+\s*[)]'
re_pat_inst_sv = re.compile(pat_inst_sv)
re_pat_inst_v = re.compile(pat_inst_v)


def list_merge(list1, list2):
    list_new = [item for item in list1]
    for item in list2:
        list_new.append(item)
    return list_new


def find_top_module_in_file(path_to_IP_lib, filename):
    with open(os.path.join(path_to_IP_lib, filename)) as f:
        contents = f.read()
    contents = regex_patterns.re_pat_line_comment.sub('', contents)
    contents = regex_patterns.re_pat_block_comment.sub('', contents)
    module_names = regex_patterns.re_pat_module.findall(contents)
    print(module_names)
    endmodule_search = re.compile(r'endmodule')
    start_pos = 0
    end_pos = len(contents) - 1
    if len(module_names) > 0:
        mod_inst = {}
        false_count = len(module_names)
        while endmodule_search.search(contents, start_pos, end_pos) and false_count != 1:
            end_pos = endmodule_search.search(contents, start_pos, end_pos).span()[1]
            contents_temp = contents[start_pos: end_pos]
            mod_names = regex_patterns.re_pat_module.findall(contents_temp)
            mod_name = mod_names[0]
            instantiations = list_merge(mod_names, list(
                set(re_pat_inst_v.findall(contents_temp)).union(set(re_pat_inst_sv.findall(contents_temp)))))
            for instances in instantiations:
                if instances in mod_inst:
                    if instances != mod_name:
                        if not mod_inst[instances]:
                            mod_inst[instances] = True
                            false_count -= 1
                        else:
                            continue
                else:
                    if instances != mod_name:
                        mod_inst[instances] = True
                        false_count -= 1
                    else:
                        mod_inst[instances] = False
            start_pos = end_pos
            end_pos = len(contents) - 1

        result_top = []
        for mod1_name, instantiations1 in mod_inst.items():
            if not instantiations1:
                result_top.append(mod1_name)
        top_module = None
        if len(result_top) > 0:
            top_module = input(f'choose top module from given list {result_top}\n')
            while top_module is not "":
                top_module = input(f'choose top module from given list {result_top}\n')
        return top_module

    else:
        return module_names[0]



if __name__ == '__main__':
    print(find_top_module_in_file('D:\Code\SoC Compiler Tool', 'SoC_Compiler_input_bus.json'))
