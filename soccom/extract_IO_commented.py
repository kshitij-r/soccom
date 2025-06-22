import os
from regex_patterns import *


class ExtractRtl:
    def __init__(self, path, filename):  #used to initialize the variables || executed everytime the class is called.
        self.path = path
        self.filename = filename
        self.inputs = list()
        self.outputs = list()
        self.inouts = list()
        self.module_names = list()
        self.parameters = list()
        self.packages = list()
        self.includes = list()

    def file_read(self):
        if (not self.filename.endswith('.v')) and (not self.filename.endswith('.sv')):
            print('Only files ending in .v or .sv should be given')
            exit(0)
        try:
            with open(os.path.join(self.path, self.filename), 'r') as file:
                f_contents = file.read()
            f_contents = re_pat_line_comment.sub('', f_contents)      #??
            f_contents = re_pat_block_comment.sub('', f_contents)
            # module_names = re_pat_module.findall(f_contents)
            temp = (re.search(r'endmodule', f_contents)).span()[1]
            f_contents = f_contents[:(temp + 1)]
        except FileNotFoundError:
            print('File not found')
        except AttributeError:
            print('There is only commented code')
        else:
            return f_contents

    def extract_headers(self):
        contents = self.file_read()
        matches_pack = re_pat_packages.findall(contents)
        matches_incl = re_pat_includes.findall(contents)
        if len(matches_pack) != 0:
            for match in matches_pack:
                if ',' in match[1]:
                    match2 = re.sub(r'\s+', '', match[1])
                    imports = match2.split(',')
                    name_header = match[0]
                    self.packages.append(tuple([name_header, tuple(imports)]))
                else:
                    self.packages.append(match)

        if len(matches_incl) != 0:
            for match in matches_incl:
                match2 = re.sub(r'([./]|\s)+', '', match)
                self.includes.append(match2.strip())

    def extract_param(self):
        contents = self.file_read()
        try:
            param_range = re.search(r'#\s*[(][^(]+[)]', contents).span()
        except AttributeError as e:
            print(e)
        else:
            matches_param = re_pat_param.findall(contents[param_range[0]:param_range[1] + 1])
            if len(matches_param) != 0:
                for matches in matches_param:
                    if matches[1][-1] == ',':
                        temp_p = matches[1][:-1].split('=')
                    else:
                        temp_p = matches[1].split('=')
                    for i in range(len(temp_p)):
                        temp_p[i] = temp_p[i].strip()

                    temp_p[0] = temp_p[0].split()
                    self.parameters.append(tuple(temp_p))

    def extract_io(self):
        contents = self.file_read()
        if self.filename.endswith('.v'):
            matches_io = re_pat_io_v.findall(contents)
        else:
            matches_io = re_pat_io_sv.findall(contents)

        if len(matches_io) == 0:
            raise IndexError('No top module inputs or outputs')
        for match in matches_io:
            if match[1] != ' ':
                if match[1][-1] == ',':
                    match2 = match[1][:-1].strip().split(',')
                else:
                    match2 = match[1].strip().split(',')
            else:
                continue
            io_type = match[0]
            if '[' in match2[0]:
                t_io_details = re.sub(r']', r'] ', match2[0])
                t_io_details = re.sub(r'\[', r' [', t_io_details)
                io_details = t_io_details.split()
            else:
                io_details = match2[0].split()
            if len(io_details) > 1:
                net_index = 0
                for net_index in range(len(io_details)-1, -1, -1):
                    if io_details[net_index].find(']') != -1:
                        continue
                    break
                io_details.append(net_index)
                if io_type == 'input':
                    self.inputs.append(tuple(io_details))
                elif io_type == 'output':
                    self.outputs.append(tuple(io_details))
                elif io_type == 'inout':
                    self.inouts.append(tuple(io_details))
                else:
                    try:
                        index_regout = self.outputs.index(tuple(io_details))
                    except ValueError:
                        pass
                    else:
                        temp = ['reg']
                        out = self.outputs[index_regout]
                        for details in out:
                            temp.append(details)
                        new_output = tuple(temp)
                        self.outputs[index_regout] = new_output
                for i in range(1, len(match2)):
                    io_details[net_index] = match2[i].strip()
                    if io_type == 'input':
                        self.inputs.append(tuple(io_details))
                    elif io_type == 'output':
                        self.outputs.append(tuple(io_details))
                    elif io_type == 'inout':
                        self.inouts.append(tuple(io_details))
                    else:
                        try:
                            index_regout = self.outputs.index(tuple(io_details))
                        except ValueError:
                            pass
                        else:
                            temp = ['reg']
                            out = self.outputs[index_regout]
                            for details in out:
                                temp.append(details)
                            new_output = tuple(temp)
                            self.outputs[index_regout] = new_output

            else:
                io_size = '[0:0]'
                for match3 in match2:
                    if io_type == 'input':
                        self.inputs.append((io_size, match3.strip(), 1))
                    elif io_type == 'output':
                        self.outputs.append((io_size, match3.strip(), 1))
                    elif io_type == 'inout':
                        self.inouts.append((io_size, match3.strip(), 1))
                    else:
                        try:
                            index_regout = self.outputs.index((io_size, match3))
                        except ValueError:
                            pass
                        else:
                            temp = ['reg']
                            out = self.outputs[index_regout]
                            for details in out:
                                temp.append(details)
                            new_output = tuple(temp)
                            self.outputs[index_regout] = new_output

    def extract_module(self):
        contents = self.file_read()
        matches_mod = re_pat_module.findall(contents)
        if len(matches_mod) == 0:
            raise IndexError('No top module inputs or outputs')
        self.module_names.append(matches_mod[0])


def main():
    obj = ExtractRtl('C:\\Users\\csury\\Desktop\\SOC_ptp', 'compute_tile_dm_spi.sv')
    obj.extract_io()
    obj.extract_module()
    obj.extract_param()
    print(f'module name is: {obj.module_names[0]}')
    # obj.extract_headers()

    print('\nparameters are')
    for i in obj.parameters:
        print(i)

    print("\ninputs are")
    for i in obj.inputs:
        print(i)

    print("\noutputs are")
    for i in obj.outputs:
        print(i)
    # for i in obj.packages:
    #     print(i)

    # for i in obj.outputs:
    #     print(i)
    #
    # for i in obj.module_names:
    #     print(i)
    # print(obj.inputs)
    # print(obj.outputs)
    # print(obj.module_names)


if __name__ == '__main__':
    main()
