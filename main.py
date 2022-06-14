# Copyright 2021 Xilinx Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bokeh.plotting import figure, curdoc
from bokeh.layouts import layout, row, column, gridplot
from bokeh.models.widgets import Tabs, Panel
from bokeh.models.annotations import Title
from bokeh.models import ColumnDataSource, DataTable, DateFormatter, TableColumn, HTMLTemplateFormatter
from bokeh.models import Button, Div, CheckboxGroup, Range1d
from bokeh.models import HoverTool
from bokeh.models import TextInput
from bokeh.models import Paragraph, Div, CustomJS
from bokeh.events import ButtonClick
from bokeh.themes import built_in_themes
from bokeh.driving import linear

from collections import deque
import subprocess
from functools import partial

import sys

from platformstats import platformstats

platformstats.init()

bg_color = '#15191C'
text_color = '#E0E0E0'

##################################################
##### Platform Stat Tab ##########################
##################################################

sample_size = 60
sample_size_actual = 60
interval = 1
x = deque([0] * sample_size)
color_list = ["darkseagreen", "steelblue", "indianred", "chocolate", "mediumpurple", "rosybrown", "gold",
              "mediumaquamarine"]


def clear_min_max():
    max_volt[:] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    max_temp[:] = [0, 0, 0]
    min_volt[:] = [7000, 7000, 7000, 7000, 7000, 7000, 7000, 7000, 7000]
    min_temp[:] = [200, 200, 200]
    global average_cpu, average_cpu_sample_size
    average_cpu = 0
    average_cpu_sample_size = 0


cpu_labels = [
    "A-53_Core_0",
    "A-53_Core_1",
    "A-53_Core_2",
    "A-53_Core_3",
]
cpu_data = {
    'A-53_Core_0': deque([0.0] * sample_size),
    'A-53_Core_1': deque([0.0] * sample_size),
    'A-53_Core_2': deque([0.0] * sample_size),
    'A-53_Core_3': deque([0.0] * sample_size),
}
volt_labels = [
    "VCC_PSPLL",
    "PL_VCCINT",
    "VOLT_DDRS",
    "VCC_PSINTFP",
    "VCC_PS_FPD",
    "PS_IO_BANK_500",
    "VCC_PS_GTR",
    "VTT_PS_GTR",
    "Total_Volt",
]
volt_data = {
    "VCC_PSPLL": deque([0] * sample_size),
    "PL_VCCINT": deque([0] * sample_size),
    "VOLT_DDRS": deque([0] * sample_size),
    "VCC_PSINTFP": deque([0] * sample_size),
    "VCC_PS_FPD": deque([0] * sample_size),
    "PS_IO_BANK_500": deque([0] * sample_size),
    "VCC_PS_GTR": deque([0] * sample_size),
    "VTT_PS_GTR": deque([0] * sample_size),
    "Total_Volt": deque([0] * sample_size),
}
temp_labels = [
    "LPD_TEMP",
    "FPD_TEMP",
    "PL_TEMP",
]
temp_data = {
    "LPD_TEMP": deque([0.0] * sample_size),
    "FPD_TEMP": deque([0.0] * sample_size),
    "PL_TEMP": deque([0.0] * sample_size),
}

# note that if a queue is not getting appended every sample, remove it from data structure, or
# popping the queue when updating sample size will not work!
mem_labels = [
    # "MemTotal",
    "MemFree",
    # "MemAvailable",
    # "SwapTotal",
    # "SwapFree",
    # "CmaTotal",
    # "CmaFree",
]
mem_data = {
    # "MemTotal": deque([0] * sample_size),
    "MemFree": deque([0] * sample_size),
    # "MemAvailable": deque([0] * sample_size),
    # "SwapTotal": deque([0] * sample_size),
    # "SwapFree": deque([0] * sample_size),
    # "CmaTotal": deque([0] * sample_size),
    # "CmaFree": deque([0] * sample_size),
}

current_data = deque([0] * sample_size)
power_data = deque([0] * sample_size)

# title
title1 = Div(
    text="""<h1 style="color :""" + text_color + """; text-align :center">Kria&trade; SOM: Hardware Platform Statistics</h1>""",
    width=550)

# average cpu display
average_cpu = 0.0
average_cpu_sample_size = 0
average_cpu_display = Div(text=str(average_cpu), width=600)

# CPU frequency display
cpu_freq_text = """<h3 style="color :""" + text_color + """;">CPU Frequencies </h3>"""
cpu_freq = [0, 0, 0, 0]
cpu_freq_display = Div(text=cpu_freq_text, width=400)

# CPU line plot
cpu_plot = figure(plot_width=800, plot_height=300, title='CPU Utilization %')
cpu_ds = [0, 0, 0, 0]
for i in range(len(cpu_labels)):
    cpu_ds[i] = (cpu_plot.line(x, cpu_data[cpu_labels[i]], line_width=2,
                               color=color_list[i], legend_label=cpu_labels[i])).data_source
cpu_plot.legend.click_policy = "hide"

# current line plot
current_plot = figure(plot_width=500, plot_height=300, title='Total SOM Current in mA')
current_ds = (current_plot.line(x, current_data, line_width=2,
                                color=color_list[0], legend_label="Current")).data_source
current_plot.legend.click_policy = "hide"

# power line plot
power_plot = figure(plot_width=500, plot_height=300, title='Total SOM Power in W')
power_ds = (power_plot.line(x, power_data, line_width=2,
                            color=color_list[0], legend_label="Power")).data_source
power_plot.legend.click_policy = "hide"

# temperature line plot
temp_plot = figure(plot_width=500, plot_height=300, title='Temperature in Celsius')
temp_ds = [0, 0, 0, 0]
temp_ds[0] = (temp_plot.line(x, temp_data[temp_labels[0]], line_width=2,
                             color=color_list[0], legend_label=temp_labels[0])).data_source
temp_plot.legend.click_policy = "hide"

# table of min/max for temperature
max_temp = [0.0, 0.0, 0.0]
min_temp = [200.0, 200.0, 200.0]
min_max_temp = dict(temp_labels=temp_labels, max_temp=max_temp, min_temp=min_temp)
min_max_temp_source = ColumnDataSource(min_max_temp)
min_max_temp_column = [
    TableColumn(field="temp_labels", title="Temperature"),
    TableColumn(field="max_temp", title="Max"),
    TableColumn(field="min_temp", title="Min")
]

temp_data_table = DataTable(source=min_max_temp_source, columns=min_max_temp_column, index_position=None,
                            width=400, height=200, background=bg_color, css_classes=['custom_table'])

# table of min/max for voltages
max_volt = [0, 0, 0, 0, 0, 0, 0, 0, 0]
min_volt = [7000, 7000, 7000, 7000, 7000, 7000, 7000, 7000, 7000]
min_max_volt = dict(volt_labels=volt_labels, max_volt=max_volt, min_volt=min_volt)
min_max_volt_source = ColumnDataSource(min_max_volt)
min_max_volt_column = [
    TableColumn(field="volt_labels", title="Voltage"),
    TableColumn(field="max_volt", title="Max"),
    TableColumn(field="min_volt", title="Min")
]

volt_data_table = DataTable(source=min_max_volt_source, columns=min_max_volt_column, index_position=None,
                            width=400, height=200, background=bg_color, css_classes=['custom_table'])

# memory line plot
mem_plot = figure(plot_width=800, plot_height=300, title='Total Free Memory in kB')
mem_ds = (mem_plot.line(x, mem_data["MemFree"], line_width=2,
                        color=color_list[0], legend_label="MemFree")).data_source
mem_plot.legend.click_policy = "hide"

# memory bar plot
mem_bar_label = ['MemUsed', 'SwapUsed', 'CMAUsed']
mem_bar_total = [0, 0, 0]
mem_bar_used = [0, 0, 0]
mem_bar_available = [0, 0, 0]
mem_bar_percent = [0.0, 0.0, 0.0]
mem_bar_dict = dict(mem_bar_label=mem_bar_label, mem_bar_total=mem_bar_total,
                    mem_bar_used=mem_bar_used, mem_bar_percent=mem_bar_percent,
                    mem_bar_available=mem_bar_available)
mem_bar_source = ColumnDataSource(mem_bar_dict)
mem_plot_hbar = figure(y_range=mem_bar_label, x_range=[0, 100], plot_width=800, plot_height=300,
                       title='Memory Usage in %')
mem_plot_hbar.xaxis.axis_label = '%Used'
mem_percent_ds = (mem_plot_hbar.hbar(y='mem_bar_label', right='mem_bar_percent',
                                     tags=mem_bar_label, source=mem_bar_source,
                                     height=.5, fill_color='steelblue',
                                     hatch_pattern='vertical_line', hatch_weight=2, line_width=0)).data_source
hover = HoverTool(tooltips=[("Total in kB:", "@mem_bar_total"), ("Used in kB:", "@mem_bar_used")])
mem_plot_hbar.add_tools(hover)

# reset button
reset_button = Button(label="Reset Min/Max and Averages", width=200, button_type='primary')
reset_button.on_click(clear_min_max)


# sample interval
def update_interval(attr, old, new):
    global interval
    interval = max(float(new), 0.5)
    global input_interval
    input_interval.value = str(interval)
    global callback
    curdoc().remove_periodic_callback(callback)
    callback = curdoc().add_periodic_callback(update, interval * 1000)


input_interval = TextInput(value=str(interval), title="input interval in seconds (minimal 0.5s):",
                           css_classes=['custom_textinput'], width=100)
input_interval.on_change('value', update_interval)


# sample size
def update_sample_size(attr, old, new):
    global sample_size, sample_size_actual
    new_sample_size = int(new)
    if new_sample_size < sample_size_actual:
        excess = sample_size_actual - new_sample_size
        while excess > 0:
            x.popleft();
            for j in range(len(cpu_labels)):
                cpu_data[cpu_labels[j]].popleft()
            for j in range(len(volt_labels)):
                volt_data[volt_labels[j]].popleft()
            for j in range(len(temp_labels)):
                temp_data[temp_labels[j]].popleft()
            for j in range(len(mem_labels)):
                mem_data[mem_labels[j]].popleft()
            excess = excess - 1
        sample_size_actual = new_sample_size
    sample_size = new_sample_size


input_sample_size = TextInput(value=str(sample_size), title="Sample Size:",
                              css_classes=['custom_textinput'], width=100)
input_sample_size.on_change('value', update_sample_size)

time = 0

# default_data_range = cpu_plot.y_range

cpu_plot.y_range = Range1d(0, 100)

mem_result1 = platformstats.get_ram_memory_utilization()  # Returns list [return_val, MemTotal, MemFree, MemAvailable]
mem_plot.y_range = Range1d(0, mem_result1[1])  # get_mem("MemTotal"))
power_plot.y_range = Range1d(0, 6)
current_plot.y_range = Range1d(0, 1000)
temp_plot.y_range = Range1d(0, 100)


# # dynamic scaling:
# def update_scaling(attr, old, new):
#     if new == [0]:
#         cpu_plot.y_range = default_data_range
#         cpu_plot.title.text = "name 1"
#     else:
#         cpu_plot.y_range = Range1d(0, 50)
#         cpu_plot.title.text = "name 2"
#
# checkbox_labels = ["Enable Dynamic Y-axis Scaling"]
# checkbox_group = CheckboxGroup(labels=checkbox_labels, active=[], css_classes=['custom_textinput'],)
# checkbox_group.on_change('active', update_scaling)


@linear()
def update(step):
    global time
    global sample_size_actual
    time = time + interval
    if sample_size_actual >= sample_size:
        x.popleft()
    x.append(time)

    read = platformstats.get_cpu_utilization()

    average_cpu_x = 0
    for j in range(len(cpu_labels)):
        if sample_size_actual >= sample_size:
            cpu_data[cpu_labels[j]].popleft()
        cpu_data_read = read[j]
        cpu_data[cpu_labels[j]].append(cpu_data_read)
        cpu_ds[j].trigger('data', x, cpu_data[cpu_labels[j]])
        average_cpu_x = average_cpu_x + cpu_data_read

    # average CPU usage
    global average_cpu_sample_size, average_cpu
    average_cpu = average_cpu * average_cpu_sample_size
    average_cpu_sample_size = average_cpu_sample_size + 1
    average_cpu = (average_cpu + (average_cpu_x / 4)) / average_cpu_sample_size

    text = """<h2 style="color :""" + text_color + """;">""" + \
           "&nbsp; &nbsp; Average CPU utilization over last " + str(average_cpu_sample_size) + \
           " samples is " + str(round(average_cpu, 2)) + """%</h2>"""
    average_cpu_display.text = text

    # CPU frequency
    cpu_freq = []

    for j in range(4):
        cpu_freq.append(str(platformstats.get_cpu_frequency(j)[1]))  # //Returns list [return_val, cpu_freq]
        # cpu_freq.append(open('/sys/devices/system/cpu/cpu' + str(j) + '/cpufreq/cpuinfo_cur_freq', 'r').read())

    cpu_freq_display.text = cpu_freq_text + """<p style="color :""" + text_color + """;">&nbsp; &nbsp;CPU0:""" + \
                            cpu_freq[0] + \
                            "MHz<br>&nbsp; &nbsp;CPU1:" + cpu_freq[1] + \
                            "MHz<br>&nbsp; &nbsp;CPU2:" + cpu_freq[2] + \
                            "MHz<br>&nbsp; &nbsp;CPU3:" + cpu_freq[3] + "MHz"

    volts = []
    volts = platformstats.get_voltages()  # Returns list [return_val, VCC_PSPLL, PL_VCCINT, VOLT_DDRS, VCC_PSINTFP, VCC_PS    _FPD, PS_IO_BANK_500, VCC_PS_GTR, VTT_PS_GTR, total_voltage]
    volts.pop(0)

    for j in range(len(volt_labels)):
        if sample_size_actual >= sample_size:
            volt_data[volt_labels[j]].popleft()
        volt_read = int(volts[j])
        volt_data[volt_labels[j]].append(volt_read)
        if (volt_read < min_volt[j]) or (volt_read > max_volt[j]):
            min_volt[j] = min(min_volt[j], int(volts[j]))
            max_volt[j] = max(max_volt[j], int(volts[j]))
            volt_data_table.source.trigger('data', volt_data_table.source, volt_data_table.source)

    temperatures = []
    temperatures = platformstats.get_temperatures()  # Returns list [return_val, LPD_TEMP, FPD_TEMP, PL_TEMP]
    temperatures.pop(0)
    for j in range(len(temp_labels)):
        if sample_size_actual >= sample_size:
            temp_data[temp_labels[j]].popleft()
        temperature_read = (float(temperatures[j])) / 1000
        temp_data[temp_labels[j]].append(temperature_read)
        if (temperature_read < min_temp[j]) or (temperature_read > max_temp[j]):
            min_temp[j] = min(min_temp[j], temperature_read)
            max_temp[j] = max(max_temp[j], temperature_read)
            temp_data_table.source.trigger('data', temp_data_table.source, temp_data_table.source)
    temp_ds[0].trigger('data', x, temp_data[temp_labels[0]])

    ina260_current = platformstats.get_current()[1]  # Returns list [return_val, total_current

    if sample_size_actual >= sample_size:
        current_data.popleft()
    current_data.append(int(ina260_current))
    current_ds.trigger('data', x, current_data)

    ina260_power = (platformstats.get_power()[1] / 1000000)  # Returns list [return_val, total_power]
    if sample_size_actual >= sample_size:
        power_data.popleft()
    power_data.append(ina260_power)
    power_ds.trigger('data', x, power_data)

    # Mem line chart
    mem_result1 = platformstats.get_ram_memory_utilization()  # Returns list [return_val, MemTotal, MemFree, MemAvailable]
    mem_result2 = platformstats.get_swap_memory_utilization()  # Returns list [return_val, SwapTotal, SwapFree]
    mem_result3 = platformstats.get_cma_utilization()  # Returns list [return_val, CmaTotal, CmaFree]
    mem_num = mem_result1[2]  # get_mem("MemFree")
    if sample_size_actual >= sample_size:
        mem_data["MemFree"].popleft()
    mem_data["MemFree"].append(mem_num)
    mem_ds.trigger('data', x, mem_data["MemFree"])

    # Memory usage Horizontal bar chart
    mem_bar_total[0] = mem_result1[1]  # get_mem('MemTotal')
    mem_bar_available[0] = mem_result1[3]  # get_mem('MemAvailable')
    mem_bar_used[0] = mem_bar_total[0] - mem_bar_available[0]
    mem_bar_percent[0] = 100 * mem_bar_used[0] / max(mem_bar_total[0], 1)
    mem_bar_total[1] = mem_result2[1]  # get_mem('SwapTotal')
    mem_bar_available[1] = mem_result2[2]  # get_mem('SwapFree')
    mem_bar_used[1] = mem_bar_total[1] - mem_bar_available[1]
    mem_bar_percent[1] = 100 * mem_bar_used[1] / max(mem_bar_total[1], 1)
    mem_bar_total[2] = mem_result3[1]  # get_mem('CmaTotal')
    mem_bar_available[2] = mem_result3[2]  # get_mem('CmaFree')
    mem_bar_used[2] = mem_bar_total[2] - mem_bar_available[2]
    mem_bar_percent[2] = 100 * mem_bar_used[2] / max(mem_bar_total[2], 1)
    mem_percent_ds.trigger('data', mem_bar_label, mem_bar_percent)

    if sample_size_actual < sample_size:
        sample_size_actual = sample_size_actual + 1


# margin:  Margin-Top, Margin-Right, Margin-Bottom and Margin-Left
user_interface = column(reset_button, input_sample_size, input_interval,  # checkbox_group,
                        background=bg_color,
                        margin=(50, 50, 50, 100))
cpu_freq_block = column(cpu_freq_display,
                        background=bg_color,
                        margin=(0, 0, 0, 100))
layout1 = layout(column(row(title1, align='center'),
                        average_cpu_display,
                        row(cpu_plot, user_interface, cpu_freq_block, background=bg_color),
                        row(mem_plot, mem_plot_hbar, background=bg_color),
                        row(power_plot, current_plot, temp_plot, background=bg_color),
                        row(volt_data_table, temp_data_table, background=bg_color),
                        background=bg_color))

# Add a periodic callback to be run every 1000 milliseconds
callback = curdoc().add_periodic_callback(update, interval * 1000)

##################################################
##### Application Cockpit Tab ####################
##################################################

xlnx_config_version = subprocess.getoutput("snap info xlnx-config 2>/dev/null | sed -n \"s/^installed: *\([^ ]\+\).*/\1/p\"")
xlnx_config_prefix = "" if xlnx_config_version == "" else "xlnx-config."

## determine OS and CC
cc = subprocess.getoutput("sudo " + xlnx_config_prefix + "xmutil boardid | grep \"product\"")
if "KR" in cc and "26" in cc:
    cc = "KR260"
elif "KV" in cc and "26" in cc:
    cc = "KV260"
else:
    platformstats.deinit()
    print("ERROR", cc, " is not supported")
    exit()

os = subprocess.getoutput("cat /etc/os-release")
if "PetaLinux" in os:
    os = "petalinux"
elif "Ubuntu" in os:
    os = "ubuntu"
else:
    platformstats.deinit()
    print("ERROR", os, " is not supported")
    exit()


title2 = Div(
    text="""<h1 style="color :""" + text_color + """; text-align :center">Kria&trade; SOM: Application Cockpit</h1>""",
    width=500)


def xmutil_unloadapp():
    if current_command:
        terminate_app()
    subprocess.run(["sudo", xlnx_config_prefix + xmutil, "unloadapp"])
    draw_apps()
    # draw_app_run_buttons()
    layout2.children[4] = column(load_buttons, margin=(0, 0, 0, 50))
    layout2.children[1] = active_app_print
    # layout2.children[2] = row(run_buttons)


unload_button = Button(label="Unloadapp", width=600, button_type='primary')
unload_button.on_click(xmutil_unloadapp)


# Apps!!!!!###########################################################################################################
def xmutil_loadapp(app_name):
    if current_command:
        platformstats.deinit()
        print("\nERROR: unexpected command:", current_command, "\n")
        exit()
    command = str('sudo ' + xlnx_config_prefix + 'xmutil loadapp ' + app_name)
    subprocess.run(command, shell=True, capture_output=True)
    draw_apps()
    # draw_app_run_buttons()
    layout2.children[4] = column(load_buttons, margin=(0, 0, 0, 50))
    layout2.children[1] = active_app_print
    # layout2.children[2] = row(run_buttons)


load_buttons = []
active_app_print = Div(
    text="""<h2 style="color :""" + text_color + """; text-align :center">Active Accelerator: None</h2>""",
    width=600)
active_app = "None"


def draw_apps():
    global load_buttons
    global active_app_print
    global active_app
    active_app = "None"

    listapp_output = subprocess.run(['sudo ' + xlnx_config_prefix + 'dfx-mgr-client -listPackage'], shell=True,
                                    stdout=subprocess.PIPE).stdout.decode("utf-8")

    listapp = listapp_output.split("\n")
    apps = []
    load_buttons = []
    for i in range(len(listapp) - 1):
        x = listapp[i].split()
        if x and x[0] != "Accelerator":
            apps.append(x[0])
            if x[5] != "-1":
                active_app = x[0]

    active_app_print = Div(
        text="""<h2 style="color :""" + text_color + """; text-align :center">Active Accelerator: """ + active_app + """</h2>""",
        width=600)

    for i in range(len(apps)):
        load_buttons.append(Button(label=apps[i], width=300, button_type='primary'))
        if active_app != "None":
            if apps[i] == active_app:
                load_buttons[i].button_type = 'success'
                load_buttons[i].js_on_click(
                    CustomJS(code='alert("This Accelerator is already loaded, Unloadapp first!");'))
            else:
                load_buttons[i].button_type = 'default'
                load_buttons[i].js_on_click(CustomJS(code='alert("Unloadapp First!");'))
        else:
            load_buttons[i].on_click(partial(xmutil_loadapp, app_name=apps[i]))


app_print = Div(
    text="""<h2 style="color :""" + text_color + """; text-align :left">Available Accelerated Applications on
     target to load</h2><h4 style="color :""" + text_color + """; text-align :left">&emsp;&emsp;Blue - click
    to load, Green - Loaded Accelerator, White - available to load after unloading</h4>""", width=1600)
draw_apps()
current_command = None


def terminate_app():
    global current_command
    current_command.terminate()
    current_command = None


def run_app(run_command):
    global current_command
    if current_command:
        terminate_app()
    print("run_command:", run_command, "\n\n")
    current_command = subprocess.Popen(run_command, shell=True)
    print("\n\ncurrent command: ", current_command, "\n\n")


# run_buttons = []
#
#
# def draw_app_run_buttons():
#     global run_buttons
#     global active_app
#     run_buttons = []
#     if active_app == "None":
#         return
#     less_cmd = 'less som_dashboard/commands/' + active_app + '_cmds.txt'
#     print(less_cmd)
#     less_return = subprocess.run(less_cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
#     run_commands_txt = less_return.stdout.decode("utf-8")
#     if "No such file" in run_commands_txt:
#         return
#     run_commands = run_commands_txt.split('\n')
#     for commands in run_commands:
#         x = commands.split(',')
#         button = Button(label=x[0], width=300, button_type='primary')
#         button.on_click(partial(run_app, run_command=x[1]))
#         run_buttons.append(button)
#
#
# draw_app_run_buttons()

# packages!!###########################################################################################################

package_print = Div(
    text="""<h2 style="color :""" + text_color + """; text-align :center">Available Accelerated Application
    Packages, click button below to download and install the chosen package</h2>""", width=1600)


def dnf_install(app_name):
    if "ubuntu" in os:
        command = str('sudo apt install ' + app_name + " -y")

    elif "petalinux" in os:
        command = str('sudo dnf install ' + app_name + " -y")

    else:
        platformstats.deinit()
        print("ERROR: OS is not what we expected", os)
        exit()

    subprocess.call(command, shell=True)
    draw_pkgs()
    layout2.children[6] = column(pkgs_buttons, margin=(0, 0, 0, 50))
    draw_apps()
    layout2.children[4] = column(load_buttons, margin=(0, 0, 0, 50))


pkgs_buttons = []


def draw_pkgs():
    global pkgs_buttons
    if "ubuntu" in os:
        temp_cmd = str("apt-cache search " + cc)
    elif "petalinux" in os:
        temp_cmd = str("sudo " + xlnx_config_prefix + "xmutil getpkgs | grep packagegroup-" + cc)

    else:
        platformstats.deinit()
        print("ERROR: OS is not what we expected", os)
        exit()

    getpkgs_output = subprocess.run([temp_cmd], shell=True,
                                    stdout=subprocess.PIPE).stdout.decode("utf-8")
    list_pkgs = getpkgs_output.split("\n")
    pkgs_buttons = []
    for i in range(len(list_pkgs) - 1):
        x = list_pkgs[i].split()
        pkgs_buttons.append(Button(label=x[0], width=300, button_type='primary'))
        pkgs_buttons[i].on_click(partial(dnf_install, app_name=x[0]))


draw_pkgs()

app_print2 = Div(
    text="""<h3 style="color :""" + text_color + """; text-align :center">To execute application, use command
    line or start Jupyter lab and use Jupyter notebooks. </h3>""", width=1600)

layout2 = layout([
    row(title2, align='center'),  # 0
    [active_app_print],  # 1
    # row(run_buttons),  # 2
    column(unload_button, margin=(0, 0, 0, 50)),  # 2
    [app_print],  # 3
    column(load_buttons, margin=(0, 0, 0, 50)),  # 4
    [package_print],  # 5
    column(pkgs_buttons, margin=(0, 0, 0, 50)),  # 6
    row(app_print2, margin=(100, 0, 400, 0))
])
layout2.background = bg_color

##################################################
##### Group Tabs        ##########################
##################################################

curdoc().theme = 'dark_minimal'
tab1 = Panel(child=layout1, title="Platform Statistic Dashboard")
tab2 = Panel(child=layout2, title="Application Cockpit")
tabs = Tabs(tabs=[tab1, tab2])
curdoc().add_root(tabs)

