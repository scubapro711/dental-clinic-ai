/** @odoo-module **/

import { Component, useState ,onMounted} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { useBus, useService } from "@web/core/utils/hooks"; 


var selected_surface = [];
var selected_tooth = '';
var selected_treatment = '';
var treatment_lines = new Array();
var dentist_id = '';
var user_name = '';
var operation_id = 0;
var is_tooth_select = false
var selected_category = '';
var full_mouth_teeth = new Array();
var Missing_Tooth = 0;
var NO_OF_TEETH = 32;
var cont = true;
var update = false;
var other_patient_history = new Array();
var action_on_teeth = new Array();
var Palmer;
var Iso;
var type = '';
var full_mouth_selected = 0;
var patient_id;
var appt_id;
var dentist_name;
var currentlySelectedTreatment = null
// var counter = 0;
// self.get_user(session.partner_id);


export class DentalChartAction extends Component {
  
    
    setup() {
        super.setup();
        this.context = useState(this.props.action.context);
        this.actionService = useService("action");
        this.orm = useService("orm");
        // this.rpc = useService('rpc');
        onMounted(this.onMounted);
    }

    onMounted() {
        this.patient_history();
        this.get_treatment_cats();
        this.renderElement();
        this.buttons();
    }


    async patient_history() {
        var Missing_Tooth = 0;
        var cnt = 1;
        var cnt2 = 1;
        var surface2_cnt = 32;
        var tooth2_cnt = 32;
        var self = this;
        const activeId = this.context.active_id;
        const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id,activeId], {});
        type = data.type;
        patient_id = data.patient_id;
        appt_id = data.appt_id;
        dentist_id = data.dentist_id;
        dentist_name = data.dentist_name;
        var data_take = await this.orm.call('medical.patient', 'history_take', [0], {patient_id})
        try{
            if (data_take){
                for (var i=0;i<data_take.length;i++){
                    if (data_take[i].state != 'completed'){
                var create_date = data_take[i].date;
                var surface =data_take[i].surface.replace(/^\[|\]$/g, '');
                surface = surface.replace(/'/g, '');                
                surface = surface.split(',')                
                var full_tooth = data_take[i].teeth_code_rel_ids;
                var newArray = surface.map(function(item) {
                    return item.replace(/ /g, ''); // Replace spaces with an empty string
                });
                // selected_surface.push(data_take[i].description);
                var teeth_id = data_take[i].teeth_id;                
                var state = data_take[i].state;
                var dentist = data_take[i].dentist;
                var detail_description = data_take[i].detail_description.split(' ');
                var description ={}
                description["treatment_name"]=data_take[i].description_id;
                description['amount'] = data_take[i].amount
                description['action'] = "action";
                description['treatment_id']= data_take[i].treatment_id;
                
                if(!teeth_id){
                    this.put_data_full_mouth(self, full_tooth, true, description, state, create_date, true, false);
            
                }else{
                    this.put_data(self, detail_description, teeth_id, newArray, state, create_date, true, false, description);
                }
            }
        }
    }

        }
        catch(e){
            console.error("error catched-------------------------------",e)

        }

        if (type == 'palmer') {
            
            var palmer = {
                '1' : '8-1x',
                '2' : '7-1x',
                '3' : '6-1x',
                '4' : '5-1x',
                '5' : '4-1x',
                '6' : '3-1x',
                '7' : '2-1x',
                '8' : '1-1x',
                '9' : '1-2x',
                '10' : '2-2x',
                '11' : '3-2x',
                '12' : '4-2x',
                '13' : '5-2x',
                '14' : '6-2x',
                '15' : '7-2x',
                '16' : '8-2x',
                '17' : '8-3x',
                '18' : '7-3x',
                '19' : '6-3x',
                '20' : '5-3x',
                '21' : '4-3x',
                '22' : '3-3x',
                '23' : '2-3x',
                '24' : '1-3x',
                '25' : '1-4x',
                '26' : '2-4x',
                '27' : '3-4x',
                '28' : '4-4x',
                '29' : '5-4x',
                '30' : '6-4x',
                '31' : '7-4x',
                '32' : '8-4x',

            };
            Palmer = palmer;
        }

        if (type == 'iso') {            
            var iso = {
                '1' : '18',
                '2' : '17',
                '3' : '16',
                '4' : '15',
                '5' : '14',
                '6' : '13',
                '7' : '12',
                '8' : '11',
                '9' : '21',
                '10' : '22',
                '11' : '23',
                '12' : '24',
                '13' : '25',
                '14' : '26',
                '15' : '27',
                '16' : '28',
                '17' : '38',
                '18' : '37',
                '19' : '36',
                '20' : '35',
                '21' : '34',
                '22' : '33',
                '23' : '32',
                '24' : '31',
                '25' : '41',
                '26' : '42',
                '27' : '43',
                '28' : '44',
                '29' : '45',
                '30' : '46',
                '31' : '47',
                '32' : '48',
            };
            Iso = iso;
        }

        for (var t = 1; t <= NO_OF_TEETH; t++) {
            
            var NS = 'http://www.w3.org/2000/svg';
            var svg = document.getElementById('svg_object');
            
            if (cnt <= 16) {//devided teeths into 2 sections
                var path1_1 = 34.95833333333337;
                var path1_2 = 21.250000000000007;
                var path2_1 = 25.513888888888914;
                var path2_2 = 31.875000000000007;
                var path3_1 = 34.95833333333337;
                var path3_2 = 46.04166666666665;
                var path4_1 = 52.666666666666686;
                var path4_2 = 31.875000000000007;
                var path5_1 = 34.958333333333385;
                var path5_2 = 31.875000000000007;

                var source_img = '<img class = "teeth" src = "/pragtech_dental_management/static/src/img/tooth' + t + '.png" id = ' + t + ' width = "46" height = "50"/>';
                var missing = 0;
                for (var m = 0; m < Missing_Tooth.length; m++) {
                    if (t == Missing_Tooth[m]) {
                        missing = 1;
                        // var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/images.png" id = ' + t + ' width = "46" height = "50"/>';
                        var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/tooth' + t + '.png" id = ' + t + ' width = "46" height = "50" style="visibility:hidden"/>';
                    }
                }
                
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = source_img;
                document.getElementById('teeth-surface-1').appendChild(tempDiv);
                if (cnt == 0) {//hardcode first rectangular coordinates
                    
                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view buccal " + cnt + '_buccal 0');
                    newElement.setAttribute("id", "view_" + cnt + "_top");
                    
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + path1_1 + " " + path1_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + path2_1 + " " + path2_2 + ")");
                    newElement.setAttribute("class", "view distal " + cnt + '_distal 0');
                    newElement.setAttribute("id", "view_" + cnt + "_left");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view lingual " + cnt + '_lingual 0');
                    newElement.setAttribute("id", "view_" + cnt + "_bottom");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + path3_1 + " " + path3_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view mesial " + cnt + '_mesial 0');
                    newElement.setAttribute("id", "view_" + cnt + "_right");
                    newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + path4_1 + " " + path4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);
                    
                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view occlusal " + cnt + '_occlusal 0');
                    newElement.setAttribute("id", "view_" + cnt + "_center");
                    newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + path5_1 + " " + path5_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                } else {
                    var top,
                        bottom,
                        right,
                        left,
                        center;
                    if (cnt <= 5) {
                        top = 'buccal';
                        right = 'mesial';
                        bottom = 'lingual';
                        left = 'distal';
                        center = 'occlusal';
                    } else if (cnt <= 11) {
                        top = 'labial';
                        right = 'mesial';
                        bottom = 'lingual';
                        left = 'distal';
                        center = 'incisal';
                    } else if (cnt <= 16) {
                        top = 'buccal';
                        right = 'distal';
                        bottom = 'lingual';
                        left = 'mesial';
                        center = 'occlusal';
                    }
                }
                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + top + " " + cnt + '_' + top + ' 0');
                    newElement.setAttribute("id", "view_" + cnt + "_top");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path1_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);
                    

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + left + " " + cnt + '_' + left + ' 0');
                    newElement.setAttribute("id", "view_" + cnt + "_left");
                    newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path2_1 + (46 * (cnt - 1))) + " " + path2_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + bottom + " " + cnt + '_' + bottom + ' 0');
                    newElement.setAttribute("id", "view_" + cnt + "_bottom");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path3_1 + (46 * (cnt - 1))) + " " + path3_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + right + " " + cnt + '_' + right + ' 0');
                    newElement.setAttribute("id", "view_" + cnt + "_right");
                    newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path4_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + center + " " + cnt + '_' + center + ' 0');
                    newElement.setAttribute("id", "view_" + cnt + "_center");
                    newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + (path1_1 + (46 * (cnt - 1))) + " " + path4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                if (missing) {
                    const elements = [
                        document.getElementById('view_' + cnt + '_top'),
                        document.getElementById('view_' + cnt + '_left'),
                        document.getElementById('view_' + cnt + '_bottom'),
                        document.getElementById('view_' + cnt + '_right'),
                        document.getElementById('view_' + cnt + '_center')
                    ];
                
                    elements.forEach(element => {
                        if (element) {
                            element.setAttribute('visibility', 'hidden');
                        }
                    });
                }
                
            }else {
                var p1_1 = 33.998659373659635;
                var p1_2 = 69.01321857571864;
                var p2_1 = 24.554214929215078;
                var p2_2 = 79.63821857571861;
                var p3_1 = 33.998659373659635;
                var p3_2 = 93.80488524238524;
                var p4_1 = 51.706992706992764;
                var p4_2 = 79.63821857571861;

                var source_img = '<img class = "teeth" src = "/pragtech_dental_management/static/src/img/tooth' + tooth2_cnt + '.png" id = ' + tooth2_cnt + ' width = "46" height = "50"/>';

                var missing = 0;
                for (var m = 0; m < Missing_Tooth.length; m++) {
                    if (tooth2_cnt == Missing_Tooth[m]) {
                        missing = 1;
                        // var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/images.png" id = ' + tooth2_cnt + ' width = "46" height = "50"/>';
                        var source_img = '<img class = "blank" src = "/pragtech_dental_management/static/src/img/tooth' + tooth2_cnt + '.png" id = ' + tooth2_cnt + ' width = "46" height = "50" style="visibility:hidden"/>';
                    }
                }
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = source_img;
                document.getElementById('teeth-surface-2').appendChild(tempDiv);

                if (cnt == 17) {//hardcode first rectangular coordinates
                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view lingual " + surface2_cnt + '_lingual 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p1_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view distal " + surface2_cnt + '_distal 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
                    newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + p2_1 + " " + p2_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view buccal " + surface2_cnt + '_buccal 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + p3_1 + " " + p3_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view mesial " + surface2_cnt + '_mesial 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
                    newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + p4_1 + " " + p4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view occlusal " + surface2_cnt + '_occlusal 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
                    newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + p1_1 + " " + p4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                } else {
                    var top,
                        bottom,
                        right,
                        left,
                        center;
                    if (surface2_cnt <= 21) {
                        top = 'lingual';
                        right = 'distal';
                        bottom = 'buccal';
                        left = 'mesial';
                        center = 'occlusal';
                    } else if (surface2_cnt <= 27) {
                        top = 'lingual';
                        right = 'mesial';
                        bottom = 'labial';
                        left = 'distal';
                        center = 'incisal';
                    } else {
                        top = 'lingual';
                        right = 'mesial';
                        bottom = 'buccal';
                        left = 'distal';
                        center = 'occlusal';
                    }
                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + top + " " + surface2_cnt + "_" + top + ' 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_top");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p1_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + left + " " + surface2_cnt + "_" + left + ' 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_left");
                    newElement.setAttribute("d", "M0 0 L9.444444444444457 0 L9.444444444444457 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path2_1 + (46 * (cnt2 - 1)) - 1)) + " " + p2_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + bottom + " " + surface2_cnt + "_" + bottom + ' 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_bottom");
                    newElement.setAttribute("d", "M0 0 L17.708333333333314 0 L17.708333333333314 10.625 L0 10.625 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path3_1 + (46 * (cnt2 - 1)) - 1)) + " " + p3_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);


                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + right + " " + surface2_cnt + "_" + right + ' 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_right");
                    newElement.setAttribute("d", "M0 0 L8.263888888888914 0 L8.263888888888914 14.166666666666657 L0 14.166666666666657 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path4_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);

                    var newElement = document.createElementNS("http://www.w3.org/2000/svg", 'path');
                    newElement.setAttribute("class", "view " + center + " " + surface2_cnt + "_" + center + ' 0');
                    newElement.setAttribute("id", "view_" + surface2_cnt + "_center");
                    newElement.setAttribute("d", "M0 0 L17.7083333333333 0 L17.7083333333333 14.166666666666629 L0 14.166666666666629 L0 0 Z");
                    newElement.setAttribute("transform", "matrix(1 0 0 1 " + ((path1_1 + (46 * (cnt2 - 1)) - 1)) + " " + p4_2 + ")");
                    newElement.setAttribute("fill", "white");
                    newElement.setAttribute("stroke", "black");
                    svg.appendChild(newElement);
                    

                }
                // if (missing) {
                //     $("#view_" + surface2_cnt + "_top,#view_" + surface2_cnt + "_left,#view_" + surface2_cnt + "_bottom,#view_" + surface2_cnt + "_right,#view_" + surface2_cnt + "_center").attr('visibility', 'hidden');
                // }
                if (missing) {
                    const elements = [
                        document.getElementById('view_' + surface2_cnt + '_top'),
                        document.getElementById('view_' + surface2_cnt + '_left'),
                        document.getElementById('view_' + surface2_cnt + '_bottom'),
                        document.getElementById('view_' + surface2_cnt + '_right'),
                        document.getElementById('view_' + surface2_cnt + '_center')
                    ];
                
                    elements.forEach(element => {
                        if (element) {
                            element.setAttribute('visibility', 'hidden');
                        }
                    });
                }
                




                surface2_cnt -= 1;
                tooth2_cnt -= 1;
                cnt2++;
            }
            cnt++;
            

        }
        
        other_patient_history.forEach(function(each_operation) {                
        // _.each(other_patient_history, function(each_operation) {
            if (each_operation.tooth_id){       
                         
                self.color_surfaces(svg, each_operation['surface'].split(' '), each_operation['tooth_id'], self);
            }else {   

                self.add_selection_action(each_operation['multiple_teeth']);
                each_operation.tooth_id = "-";
                if (each_operation['desc']['action'] == 'missing') {
                    self.perform_missing_action(each_operation['multiple_teeth']);
                }
            }
        });


        // Map to track IDs and their occurrences

        

       


        document.querySelectorAll("img").forEach(function(img) {
            
            img.addEventListener("click", function() {        
                if (selected_treatment || !selected_treatment) {                    
                    if (this.classList.contains('selected_tooth')) {
                        this.classList.remove('selected_tooth');
                        self.decrement_thread([
                            'view_' + this.id + '_bottom',
                            'view_' + this.id + '_center',
                            'view_' + this.id + '_right',
                            'view_' + this.id + '_left',
                            'view_' + this.id + '_top'
                        ]);
                        if (document.getElementById('view_' + this.id + '_center').classList[3] == "0")
                            document.getElementById('view_' + this.id + '_center').setAttribute('fill', 'white');
                        if (document.getElementById('view_' + this.id + '_right').classList[3] == "0")
                            document.getElementById('view_' + this.id + '_right').setAttribute('fill', 'white');
                        if (document.getElementById('view_' + this.id + '_left').classList[3] == "0")
                            document.getElementById('view_' + this.id + '_left').setAttribute('fill', 'white');
                        document.getElementById('view_' + this.id + '_top').setAttribute('fill', 'white');
                        document.getElementById('view_' + this.id + '_bottom').setAttribute('fill', 'white');
                        selected_surface.length = 0;
                    } else {
                        this.setAttribute('class', 'selected_tooth');
                        document.getElementById('view_' + this.id + '_center').setAttribute('fill', 'orange');
                        document.getElementById('view_' + this.id + '_right').setAttribute('fill', 'orange');
                        document.getElementById('view_' + this.id + '_left').setAttribute('fill', 'orange');
                        document.getElementById('view_' + this.id + '_top').setAttribute('fill', 'orange');
                        document.getElementById('view_' + this.id + '_bottom').setAttribute('fill', 'orange');
                        self.increment_thread([
                            'view_' + this.id + '_bottom',
                            'view_' + this.id + '_center',
                            'view_' + this.id + '_right',
                            'view_' + this.id + '_left',
                            'view_' + this.id + '_top'
                        ]);
                    }
                    return;
                }                
        
                // selected_tooth = this.id;
                // self.execute_create(false, self, false);
        
                // switch (selected_treatment.action) {
                //     case 'missing':
                //         if (this.classList.contains('teeth')) {
                //             this.classList.add('blank');
                //             this.style.visibility = 'hidden';
                //             document.getElementById('view_' + this.id + '_top').setAttribute('visibility', 'hidden');
                //             document.getElementById('view_' + this.id + '_left').setAttribute('visibility', 'hidden');
                //             document.getElementById('view_' + this.id + '_bottom').setAttribute('visibility', 'hidden');
                //             document.getElementById('view_' + this.id + '_right').setAttribute('visibility', 'hidden');
                //             document.getElementById('view_' + this.id + '_center').setAttribute('visibility', 'hidden');
                //         } else {
                //             this.style.visibility = 'visible';
                //             this.classList.add('teeth');
                //             document.getElementById('view_' + this.id + '_top').setAttribute('visibility', 'visible');
                //             document.getElementById('view_' + this.id + '_left').setAttribute('visibility', 'visible');
                //             document.getElementById('view_' + this.id + '_bottom').setAttribute('visibility', 'visible');
                //             document.getElementById('view_' + this.id + '_right').setAttribute('visibility', 'visible');
                //             document.getElementById('view_' + this.id + '_center').setAttribute('visibility', 'visible');
        
                //             for (var op_id = 1; op_id <= operation_id; op_id++) {
                //                 var operationElement = document.getElementById('operation_' + op_id);
                //                 if (operationElement) {
                //                     var got_op_id = operationElement.id.substr(10);
                //                     if (parseInt(document.getElementById('tooth_' + got_op_id).innerHTML) == parseInt(this.id)) {
                //                         var tr = document.getElementById('operation_' + got_op_id);
                //                         var desc_class = document.getElementById('desc_' + got_op_id).getAttribute('class');
                //                         tr.parentNode.removeChild(tr);
                //                         for (var index = 0; index < treatment_lines.length; index++) {
                //                             if (treatment_lines[index].teeth_id == this.id) {
                //                                 for (var i2 = 0; i2 < treatment_lines[index].values.length; i2++) {
                //                                     if (treatment_lines[index].values[i2].categ_id == parseInt(desc_class)) {
                //                                         treatment_lines.splice(index, 1);
                //                                         operation_id += 1;
                //                                         return;
                //                                     }
                //                                 }
                //                             }
                //                         }
                //                         break;
                //                     }
                //                 }
                //             }
                //         }
                //         break;
                //     case 'composite':
                //         // Your composite logic here
                //         break;
                //     default:
                //         break;
                // }
            });
        });


        document.querySelectorAll(".view").forEach(function(view) {
            view.addEventListener("click", function() {          
                var self = this;
                if (this.id.includes('tooth_1') || this.id.includes('view_1')) {
                }
                
                if (!cont || update) {
                    selected_surface.length = 0;
                    cont = true;
                } else {
                    if (selected_surface[0]) {
                        var tooth = selected_surface[0].split('_')[1];
                        var current_tooth = this.id.split('_')[1];
                        if (current_tooth != tooth) {
                            selected_surface.forEach(function(surface) {
                                document.getElementById(surface).setAttribute('fill', 'white');
                            });
                            selected_surface.length = 0;
                        }
                    }
                }
        
                var found_selected_operation = self.querySelector('.selected_operation');
                if (found_selected_operation) {
                    var op_id = found_selected_operation.id.split('_')[1];
                    if (document.getElementById('status_' + op_id).innerHTML == 'Completed') {
                        alert('Cannot update Completed record');
                        document.getElementById('operation_' + op_id).classList.remove('selected_operation');
                        return;
                    }
                    var s = this.classList[1];
                    if (this.id.split('_')[1] == document.getElementById('tooth_' + op_id).classList[0]) {
                        update = true;
                        var surf_old_list = document.getElementById('surface_' + op_id).innerHTML.split(' ');
                        var got = 0;
                        for (var in_list = 0; in_list < surf_old_list.length; in_list++) {
                            if (surf_old_list[in_list] == s) {
                                got = 1;
                                var index = selected_surface.indexOf(this.id);
                                selected_surface.splice(index, 1);
                                document.getElementById('surface_' + op_id).innerHTML = '';
                                surf_old_list.forEach(function(sol) {
                                    if (sol != s)
                                        document.getElementById('surface_' + op_id).innerHTML += sol + ' ';
                                });
                                self.decrement_thread([this.id]);
                                break;
                            }
                        }
                        if (got == 0) {
                            document.getElementById('surface_' + op_id).innerHTML += s + ' ';
                            selected_surface.push(this.id);
                            self.increment_thread([this.id]);
                        }
                    } else {
                        update = false;
                    }
                }
        
                selected_tooth = this.id.split('_')[1];
                if (1) {
                    var element = document.getElementById(this.id);
                    if (element.getAttribute('fill') == 'white') {
                        element.setAttribute('fill', 'orange');
                        var available = selected_surface.indexOf(this.id);
                        if (available == -1 && is_tooth_select == false) {
                            selected_surface.push(this.id);
                        }
                    } else if (parseInt(element.classList[3]) == 0) {
                        is_tooth_select = false;
                        element.setAttribute('fill', 'white');
                        var index = selected_surface.indexOf(this.id);
                        selected_surface.splice(index, 1);
                    } else {
                        if (element.getAttribute('fill') == 'orange') {
                            element.setAttribute('fill', 'white');
                            is_tooth_select = true;
                            var current_tooth_id = this.id.lastIndexOf("_");
                            var res = this.id.slice(current_tooth_id, this.id.length);
                        } else {
                            selected_surface.push(this.id);
                        }
                    }
                }
            });
        });


    }

    async window_close() {
        // Perform the action to open the window with the desired form and kanban views
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'medical.patient',
            views: [[false, 'form'], [false, 'kanban']],
            res_id: patient_id,  // Assuming 'patient_id' is defined elsewhere
            target: 'current'
        });
    
        // Navigate back in the history
        this.env.config.historyBack();
    
        const activeId = this.context.active_id;
        const listData = [];
    
        // Fetch data from the server using the 'medical.patient' model's 'get_data' method
        const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id, activeId], {});
        const apptId = data.appt_id;
    }
    
    async perform_action() {               
        const activeId = this.context.active_id;
        const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id, activeId], {});
        const appt_id = data.appt_id;
        const $def = new Promise(resolve => resolve());
        const treatmentLines = [];
    
        for (let op = 1; op <= operation_id; op++) {
            const opId = document.getElementById('operation_' + op);
            if (opId) {
                opId.classList.remove('selected_operation');
    
                const teethId = document.getElementById('tooth_' + op);
                const createdDate = document.getElementById('date_time_' + op);
                const prevRecord = document.getElementById('previous_' + op);
                const statusId = document.getElementById('status_' + op);
                const surfaceElement = document.getElementById('selected_surface_' + op);
                const surfaceName = surfaceElement ? surfaceElement.innerText : '';                
                const statusName = statusId ? statusId.getAttribute('status_name') : '';
                const dateElement = document.getElementById('date_time_' + op);
                const dateText = dateElement ? dateElement.innerText.trim() : '';
                const dentist = document.getElementById('dentist_' + op);
                const surface = document.getElementById('surface_' + op);                
                const desc = document.getElementById('desc_' + op);
                const categId = desc ? desc.className : '';
                const surfaceList = surface ? surface.innerHTML.split(' ') : [];
                const tooth = teethId ? teethId.className : '';
                const allTeeth = opId.className;
                const vals = surfaceList.map(eachSurface => eachSurface);
                const position = vals.indexOf('<p');
                for (let i = 1; i < position; i++) {
                    vals[0] += ' ' + vals[i];
                }
    
                const categList = [{
                    'categ_id': categId,
                    'values': vals[0] || ''
                }];
    
                const actualTooth = teethId ? teethId.id : '';
    
                treatmentLines.push({
                    'date': dateText,
                    'status': statusId ? statusId.innerHTML : '',
                    'status_name': statusName,
                    'teeth_id': tooth,
                    'dentist': user_name,
                    'values': categList,
                    'prev_record': prevRecord ? prevRecord.innerHTML : '',
                    'multiple_teeth': allTeeth,
                    'selected_area': surfaceName,
                });     
                
                // Assuming treatmentLines is an array of objects
                for (const treatment of treatmentLines) {
                }

    
                if (statusName === "completed") {
                    const operationElement = document.getElementById('operation_' + op);
                    if (operationElement) {
                        operationElement.remove();
                    }
                }
            }
        }
    
        try {
            const res = await this.orm.call('medical.patient', 'create_lines', [patient_id, treatmentLines, patient_id, appt_id], {});
            treatmentLines.length = 0;
            return res;
        } catch (error) {
            console.error('Error:', error);
            return $def;
        }
    }
    


   
    async buttons(){
        const self = this;
        document.querySelectorAll('.close').forEach(function(closeButton) {
            closeButton.addEventListener('click', function(e) {
                self.perform_action().then(function() {
                    self.window_close();
                });
            });
        });
        document.getElementById('select_full_mouth').addEventListener('change', function(e) {
            
            full_mouth_selected = this.checked ? 1 : 0;
            
            let miss = 0;
            let full_mouth = [];
        
            for (let select_all_tooth = 1; select_all_tooth <= 32; select_all_tooth++) {                
                miss = 0;
                            
                
                for (let each_from_missing = 0; each_from_missing < Missing_Tooth.length; each_from_missing++) {
                    
                    if (Missing_Tooth[each_from_missing] === select_all_tooth) {
                        miss = 1;
                        break;
                    }
                }
        
                if (!miss && full_mouth_selected) {    
                    full_mouth.push(select_all_tooth); 
                    
                    
                    document.getElementById('view_' + select_all_tooth + "_center").setAttribute('fill', 'orange');
                    document.getElementById('view_' + select_all_tooth + "_top").setAttribute('fill', 'orange');
                    document.getElementById('view_' + select_all_tooth + "_right").setAttribute('fill', 'orange');
                    document.getElementById('view_' + select_all_tooth + "_left").setAttribute('fill', 'orange');
                    document.getElementById('view_' + select_all_tooth + "_bottom").setAttribute('fill', 'orange');
                
                } else if (!miss && !full_mouth_selected) {           
                            
                    full_mouth.push(select_all_tooth);                    
                    document.getElementById('view_' + select_all_tooth + "_center").setAttribute('fill', 'white');
                    document.getElementById('view_' + select_all_tooth + "_top").setAttribute('fill', 'white');
                    document.getElementById('view_' + select_all_tooth + "_right").setAttribute('fill', 'white');
                    document.getElementById('view_' + select_all_tooth + "_left").setAttribute('fill', 'white');
                    document.getElementById('view_' + select_all_tooth + "_bottom").setAttribute('fill', 'white');
                }
                
            }
            full_mouth_teeth = full_mouth;
            
            
        });
        

        document.querySelectorAll('.myButton').forEach(button => {
            button.addEventListener('click', function(e) {                
                
                const current_obj = this;
                const found = document.querySelectorAll('.selected_operation .progress_table_actions');
                
                if (found.length === 0) {
                    alert('Please select a record!');
                    return;
                }
        
                found.forEach(function(each_found, index) {
                    if (each_found.innerText !== 'missing') {
                        const actual_id = each_found.id.substr(7);
        
                        const statusElement = document.getElementById('status_' + actual_id);
                        
                        if (statusElement) {
                            const statusName = statusElement.getAttribute('status_name');
                            if (statusName !== 'completed') {
                                statusElement.setAttribute('status_name', current_obj.id);
                                statusElement.innerHTML = current_obj.innerHTML.trim();
                            } else if (statusName === 'completed') {
                                statusElement.innerHTML = document.getElementById('completed').textContent.trim();
                            }
                        } else {
                            console.error('Element not found: status_' + actual_id);
                        }
                    }
                });
            });
        });
    

    }



    async renderElement(parent, options) {
        const self = this;
    
        try {
            const patientId = this.context.active_id;
            
            // Fetch the teeth codes and patient data
            const teethCodes = await this.orm.call('teeth.code', 'get_teeth_code', [patientId], {});
            const patientData = await this.orm.call('medical.patient', 'get_data', [patientId, patientId], {});
            const type = patientData.type;
    
            // Get references to the upper and lower teeth containers
            const upperTeeths = document.getElementById('upper_teeths');
            const lowerTeeths = document.getElementById('lower_teeths');
    
            // Clear existing content in upper and lower teeth containers before appending new data
            upperTeeths.innerHTML = '';
            lowerTeeths.innerHTML = '';
    
            let name = '';
            let j = 0;
            let k = 7;
            let l = 0;
    
            if (type === 'universal') {
                for (let i = 0; i < 16; i++) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    upperTeeths.insertAdjacentHTML('beforeend', name);
                }
                for (let i = 31; i > 15; i--) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    lowerTeeths.insertAdjacentHTML('beforeend', name);
                }
            } else if (type === 'palmer') {
                for (let i = 7; i >= 0; i--) {
                    name = `<td width="47px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    upperTeeths.insertAdjacentHTML('beforeend', name);
                }
                for (let i = 7; i < 15; i++) {
                    name = `<td width="47px" id="teeth_${i}">${teethCodes[j]}</td>`;
                    upperTeeths.insertAdjacentHTML('beforeend', name);
                    j++;
                }
                for (let i = 23; i > 15; i--) {
                    name = `<td width="47px" id="teeth_${i}">${teethCodes[k]}</td>`;
                    lowerTeeths.insertAdjacentHTML('beforeend', name);
                    k--;
                }
                for (let i = 24; i < 32; i++) {
                    name = `<td width="47px" id="teeth_${i}">${teethCodes[l]}</td>`;
                    lowerTeeths.insertAdjacentHTML('beforeend', name);
                    l++;
                }
            } else if (type === 'iso') {
                for (let i = 0; i <= 7; i++) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    upperTeeths.insertAdjacentHTML('beforeend', name);
                }
                for (let i = 8; i <= 15; i++) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    upperTeeths.insertAdjacentHTML('beforeend', name);
                }
                for (let i = 31; i >= 24; i--) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    lowerTeeths.insertAdjacentHTML('beforeend', name);
                }
                for (let i = 23; i >= 16; i--) {
                    name = `<td width="46px" id="teeth_${i}">${teethCodes[i]}</td>`;
                    lowerTeeths.insertAdjacentHTML('beforeend', name);
                }
            }
        } catch (error) {
            console.error('An error occurred:', error);
        }
    }
    
    async get_treatment_cats() {
        
        const self = this;
        var is_tooth_select = false
        const activeId = this.context.active_id;

        const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id,activeId], {});

        patient_id = data.patient_id;
        dentist_name = data.dentist_name
        try {
            const res = await this.orm.call('product.category', 'get_treatment_categs', [patient_id], {})
            const treatment_list = res;
            
            let total_list_div = '';
            const searchBar = document.getElementById('searchBar');
            const searchButton = document.getElementById('searchButton');
        
        searchBar.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent default form submission
                searchButton.click(); // Trigger the search button click event
            }
        });

        total_list_div = ''; // Clear previous results

        searchButton.addEventListener('click', (event) => {
            event.preventDefault();
            const searchTerm = searchBar.value.toLowerCase(); // Get search term and lowercase it for case-insensitive search
        
            let total_list_div = ''; // Clear previous results
        
            // Loop through each category
            for (let j = 0; j < treatment_list.length; j++) {
                let categoryHasMatches = false; // Flag to track if the category has any matching treatments
        
                let categoryHtml = `
                    <div class="panel-heading">
                        <h4 class="panel-title">
                            <a id="categ_${treatment_list[j].treatment_categ_id}" data-bs-toggle="collapse" href="#collapse${treatment_list[j].treatment_categ_id}">
                                ${treatment_list[j].name}
                            </a>
                        </h4>
                    </div>`;
        
                let treatmentsHtml = `<div id="collapse${treatment_list[j].treatment_categ_id}" class="collapse">
                    <div class="panel-body">`;
        
                // Loop through treatments in each category
                treatment_list[j].treatments.forEach(each_one => {
                    const treatmentName = each_one['treatment_name'].toLowerCase(); // Lowercase treatment name for comparison
                    if (treatmentName.includes(searchTerm)) { // Check if the treatment name contains the search term
                        categoryHasMatches = true; // Set the flag to true if a match is found
                        treatmentsHtml += `
                            <li id="treat_${treatment_list[j].treatment_categ_id}_${each_one['treatment_id']}" class="treatment-item">
                                ${each_one['treatment_name']}
                            </li>`;
                    }
                });
        
                treatmentsHtml += `</div></div>`;
        
                if (categoryHasMatches) { // Only append category and treatments if there are matches
                    total_list_div += categoryHtml + treatmentsHtml;
                }
            }
        
            // Append the filtered content to the DOM
            const totalListDivElement = document.getElementById('total_list_div');
            totalListDivElement.innerHTML = total_list_div; // Directly update innerHTML
        
            // Add event listeners to the dynamically created treatment items
            const treatmentItems = totalListDivElement.querySelectorAll('.treatment-item');
        
            // Searched treatment click to create table
            treatmentItems.forEach(element => {
                element.addEventListener('click', () => {
                    const elementId = element.id;
                    const parts = elementId.split('_');
                    if (parts.length < 3) return; // Ensure correct ID format
                    
                    const categ_no = parts[1];
                    const treatment_id = parts[2];
        
                    // Find the corresponding treatment from self.categ_list
                    const category = self.categ_list.find(cat => cat.treatment_categ_id == categ_no);
                    if (!category) return;
                    
                    const treatment = category.treatments.find(treat => treat.treatment_id == treatment_id);
                    if (!treatment) return;
        
                    // Handle full mouth selection
                    if (full_mouth_selected == 1) {
                        self.put_data_full_mouth(self, full_mouth_teeth, full_mouth_selected, treatment, false, false, false, false);
                        return;
                    }
        
                    let found_selected_tooth = document.querySelector('.selected_tooth');
                    if (found_selected_tooth) {
                        selected_surface.length = 0; // Clear selected surfaces
                    }
        
                    if (selected_surface.length > 0) {                                    
                        if (treatment.action !== 'missing') {
                            document.querySelectorAll('.selected_treatment').forEach(el => el.classList.remove('selected_treatment'));
                            element.classList.add('selected_treatment');
                            selected_treatment = treatment;

                            let prevTreatmentId = null;
                                                
                            // Iterate over the selected surface IDs to find the treatment ID
                            selected_surface.forEach((elementId) => {
                                var elem = document.getElementById(elementId);
                                if (elem && elem.hasAttribute('data-treatment-id')) {
                                    prevTreatmentId = parseInt(elem.getAttribute('data-treatment-id'));
                                }
                            });
                    
                            // Ensure prevTreatmentId is not null before making the ORM call
                            if (prevTreatmentId) {
                                
                                let selfInstance = self; // Store reference to self
                                
                                selfInstance.orm.call('product.product', 'get_excluded_treatments', [prevTreatmentId], {}).then((prevTreatmentExcluded) => {
                                    if (prevTreatmentExcluded[2] && prevTreatmentExcluded[2].includes(selected_treatment.treatment_id)) {
                                        alert('Selected treatment is excluded!');
                                    } else {
                                        // Only execute if the treatment is NOT excluded
                                        handleExecuteCreate();
                                    }
                                });
                            } else {
                                console.warn('No valid prevTreatmentId found.');
                                handleExecuteCreate();
                            }
                            function handleExecuteCreate() {
                                self.execute_create(true, self, selected_surface);
                            }
                        } else {
                            const answer = confirm('Complete tooth has to be missing, not the selected surfaces.\nClick OK to remove the complete tooth');
                            if (answer) {
                                const tooth_id = selected_surface[0].split('_')[1];
                                document.getElementById(tooth_id).classList.add('selected_tooth');
                            }
                        }
                    } else {
                        if (found_selected_tooth) {
                                 const found = document.querySelector('.selected_treatment');
                                    if (found) found.classList.remove('selected_treatment');
                                    element.classList.add('selected_treatment');
                                    selected_treatment = treatment;
                            const selectedTeeth = document.querySelectorAll('.selected_tooth');
                            selectedTeeth.forEach(each_found_selected_tooth => {
                                selected_tooth = each_found_selected_tooth.id;
        
                                // Process selected surfaces for the selected tooth
                                ['top', 'bottom', 'left', 'right', 'center_left_0', 'center_left_1', 'center_right'].forEach(pos => {
                                    document.querySelectorAll(`[id^="view_${found_selected_tooth.id}_${pos}"]`).forEach(box => {
                                        if (box.getAttribute('fill') === 'orange') {
                                            selected_surface.push(box.id);
                                        }
                                    });
                                });
                                
                                // Variable to store the previous treatment ID
                                let prevTreatmentId = null;
                                                
                                // Iterate over the selected surface IDs to find the treatment ID
                                selected_surface.forEach((elementId) => {
                                    var elem = document.getElementById(elementId);
                                    if (elem && elem.hasAttribute('data-treatment-id')) {
                                        prevTreatmentId = parseInt(elem.getAttribute('data-treatment-id'));
                                    }
                                });
                        
                                // Ensure prevTreatmentId is not null before making the ORM call
                                if (prevTreatmentId) {
                                    
                                    let selfInstance = self; // Store reference to self
                                    
                                    selfInstance.orm.call('product.product', 'get_excluded_treatments', [prevTreatmentId], {}).then((prevTreatmentExcluded) => {
                                        if (prevTreatmentExcluded[2] && prevTreatmentExcluded[2].includes(selected_treatment.treatment_id)) {
                                            alert('Selected treatment is excluded!');
                                        } else {
                                            // Only execute if the treatment is NOT excluded
                                            handleExecuteCreate();
                                        }
                                    });
                                } else {
                                    console.warn('No valid prevTreatmentId found.');
                                    handleExecuteCreate(); // Proceed normally if there's no prevTreatmentId
                                }
                                
                                // Function to handle the execution logic
                                function handleExecuteCreate() {
                                    // Handle the 'missing' action for the selected treatment
                                    if (treatment.action === 'missing') {
                                        Missing_Tooth.push(parseInt(found_selected_tooth.id));
                                        self.perform_missing_action([found_selected_tooth.id]);
                                    }
            
                                    self.execute_create(true, self, selected_surface);
                                    found_selected_tooth.classList.remove('selected_tooth');
                                }
                            });
                        } else {
                            alert('Please select a surface or tooth first!');
                        }
                    }
                });
            });
        
            self.categ_list = treatment_list; // Optionally update categ_list if necessary
        });
        const clearButton = document.getElementById('clearButton');
        clearButton.addEventListener('click', (event) => {
            // Reset the search bar and clear any search term
            document.getElementById('searchBar').value = '';
            
            // Clear the content displayed (reset filter)
            const totalListDivElement = document.getElementById('total_list_div');
            totalListDivElement.innerHTML = ''; // Clear all filtered results

            // Optionally, you can reload all data if needed
            // Here we can either reload the full list or trigger a search with an empty string
            // Call the search functionality again with an empty search term
            searchButton.click();
        });

            for (let j = 0; j < treatment_list.length; j++) {
                total_list_div += `
                    <div class="panel-heading">
                        <h4 class="panel-title">
                            <a id="categ_${treatment_list[j].treatment_categ_id}" data-bs-toggle="collapse" href="#collapse${treatment_list[j].treatment_categ_id}">
                                ${treatment_list[j].name}
                            </a>
                        </h4>
                    </div>`;

                total_list_div += `<div id="collapse${treatment_list[j].treatment_categ_id}" class="collapse">
                    <div class="panel-body">`;

                treatment_list[j].treatments.forEach(each_one => {
                    if (each_one.action == 'missing') {
                        missing = each_one.treatment_id;
                    }

                    total_list_div += `
                        <li id="treat_${treatment_list[j].treatment_categ_id}_${each_one['treatment_id']}">
                            ${each_one['treatment_name']}
                        </li>`;
                });

                total_list_div += `</div></div>`;
                
            }            

            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = total_list_div;
            document.getElementById('total_list_div').appendChild(tempDiv);            
            self.categ_list = treatment_list;
                
            for (let i = 0; i < self.categ_list.length; i++) {                
                    
                var element = document.getElementById('categ_' + self.categ_list[i].treatment_categ_id);
                if (element) {
                    element.addEventListener('click', function() {   
                        
                        // var selected_surface = ['view_4_center'];
                        if (selected_surface) {
                            var found_selected_categ = document.querySelector('.selected_category');
                            if (found_selected_categ) {
                                found_selected_categ.classList.remove("selected_category");
                            }
                        
                            // Apply selected category styling
                            var currentCategory = document.getElementById(this.id);
                            if (currentCategory) {
                                currentCategory.classList.add('selected_category');
                            }
                            
                            var categ_no = parseInt(this.id.substr(6));
                            
                            for (var k = 0; k < self.categ_list.length; k++) {                            
                                if (self.categ_list[k].treatment_categ_id == categ_no) {                            
                                    self.categ_list[k].treatments.forEach(function(each_treatment) {                            
                                        var element = document.getElementById('treat_' + categ_no + '_' + each_treatment.treatment_id);
                                        if (element) {
                                            element.setAttribute('data-selected', 'false');
                                            element.addEventListener('click', function() {                                                
                                                if (full_mouth_selected == 1) {                                                    
                                                    self.put_data_full_mouth(self, full_mouth_teeth, full_mouth_selected, each_treatment, false, false, false, false);
                                                    return;
                                                }
                                                cont = false;
                                                var found_selected_tooth = document.querySelector('.selected_tooth'); // Updated line                            
                                                if (found_selected_tooth) {
                                                    selected_surface.length = 0;
                                                }
                            
                                                if (selected_surface.length > 0) {
                                                    if (each_treatment.action != 'missing') {
                                                        var found = document.querySelector('.selected_treatment'); // Updated line
                                                        if (found) {
                                                            found.classList.remove('selected_treatment');
                                                        }
                                                        element.classList.add('selected_treatment');
                                                        selected_treatment = each_treatment;
                                                        self.execute_create(true, self, selected_surface);
                            
                                                    } else {
                                                        var answer = confirm('Complete tooth has to be missing, not the selected surfaces.\nClick OK to remove the complete tooth');
                                                        if (answer) {
                                                            var tooth_id = selected_surface[0].split('_')[1];
                                                            document.getElementById(tooth_id).classList.add('selected_tooth');
                                                            found_selected_tooth = document.querySelector('.selected_tooth'); // Updated line
                                                        }
                                                    }
                                                }
                            
                                                if (found_selected_tooth) {
                                                    if (!found_selected_tooth){
                                                        alert('Please select the surface first!');
                                                    }else {
                                                        var found = document.querySelector('.selected_treatment'); // Updated line
                                                        if (found) {
                                                            found.classList.remove('selected_treatment');
                                                        }
                                                        element.classList.add('selected_treatment');
                                                        selected_treatment = each_treatment;
                                                        var selected_teeth = document.querySelectorAll('.selected_tooth'); // Updated line
                                                        selected_teeth.forEach(function(each_found_selected_tooth) {
                                                            selected_tooth = each_found_selected_tooth.id;
                                                            selected_surface.length = 0;
                            
                                                            if (document.getElementById('view_' + selected_tooth + '_top').getAttribute('fill') == 'orange') {
                                                                selected_surface.push('view_' + selected_tooth + '_top');
                                                            }
                                                            if (document.getElementById('view_' + selected_tooth + '_bottom').getAttribute('fill') == 'orange') {
                                                                selected_surface.push('view_' + selected_tooth + '_bottom');
                                                            }
                                                            if (document.getElementById('view_' + selected_tooth + '_center').getAttribute('fill') == 'orange') {
                                                                selected_surface.push('view_' + selected_tooth + '_center');
                                                            }
                                                            if (document.getElementById('view_' + selected_tooth + '_right').getAttribute('fill') == 'orange') {
                                                                selected_surface.push('view_' + selected_tooth + '_right');
                                                            }
                                                            if (document.getElementById('view_' + selected_tooth + '_left').getAttribute('fill') == 'orange') {
                                                                selected_surface.push('view_' + selected_tooth + '_left');
                                                            }
                            
                                                            if (each_treatment.action == 'missing') {
                                                                Missing_Tooth.push(parseInt(selected_tooth));
                                                                self.perform_missing_action([selected_tooth]);
                                                            }
                                                            self.execute_create(true, self, false);
                                                            each_found_selected_tooth.classList.remove('selected_tooth');
                                                        });
                                                        selected_surface.length = 0;
                                                    }
                                                }
                                                if (!found_selected_tooth && selected_surface.length === 0) {
                                                    
                                                    alert('Please select the surface first!');
                                                    return;
                                                }
                                            });
                                        }
                                    });
                                    break;
                                }
                            }
                            
                        } else {
                            alert('Select a tooth first!!');
                        }
                        
            });
        }
        }
    } catch (err) {
        console.error(err);
    }
}



    decrement_thread(selectedSurf) {
        selectedSurf.forEach(ss => {
            const prevCnt = document.getElementById(ss).classList[3];
            const newCnt = String(parseInt(prevCnt) - 1);
            document.getElementById(ss).classList.remove(prevCnt);
            document.getElementById(ss).classList.add(newCnt);
        });
    }
    

    increment_thread(selectedSurf) {        
        selectedSurf.forEach(ss => {
            const element = document.getElementById(ss);                        
            if (element) {
                const prevCnt = element.classList[2];
                
                const newCnt = String(parseInt(prevCnt));
                
                element.classList.remove(prevCnt);
                if (element.getAttribute("fill") === "white") {
                    element.setAttribute("fill", "orange");
                }
                element.classList.add(newCnt);
            } else {
                console.error(`Element with ID '${ss}' not found.`);
            }
        });
    }
    

    remove_selection_action(nonselection_ids) {
        nonselection_ids.forEach(each_of_nonselection_ids => {
            const elementTop = document.getElementById('view_' + String(each_of_nonselection_ids) + '_top');
            const elementBottom = document.getElementById('view_' + String(each_of_nonselection_ids) + '_bottom');
            const elementLeft = document.getElementById('view_' + String(each_of_nonselection_ids) + '_left');
            const elementRight = document.getElementById('view_' + String(each_of_nonselection_ids) + '_right');
            const elementCenter = document.getElementById('view_' + String(each_of_nonselection_ids) + '_center');
    
            if (elementTop && elementTop.classList[3] === '0') {
                elementTop.setAttribute('fill', 'white');
            }
            if (elementBottom && elementBottom.classList[3] === '0') {
                elementBottom.setAttribute('fill', 'white');
            }
            if (elementLeft && elementLeft.classList[3] === '0') {
                elementLeft.setAttribute('fill', 'white');
            }
            if (elementRight && elementRight.classList[3] === '0') {
                elementRight.setAttribute('fill', 'white');
            }
            if (elementCenter && elementCenter.classList[3] === '0') {
                elementCenter.setAttribute('fill', 'white');
            }
        });
    }
    

    checkIfToothPresent(toothId) {
        // var treatment_lines = new Array();
        for (var i = 0; i < treatment_lines.length; i++) {
            if (treatment_lines[i]['tooth_id'] == toothId) {
                return 1;
            }
        }
        return 0;    
    }

  

    get_treatment_charge(treatmentId) {
        const res = this.orm.call('product.product', 'get_treatment_charge', [treatmentId], {});
        return res;
    }


    async put_data_full_mouth(self_var, full_mouth_teeth_temp, full_mouth, selected_treatment_temp, status_to_define, created_date, is_prev_record, other_history) {
        const activeId = this.context.active_id;
        const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id,activeId], {});
        user_name = data.dentist_name
        
        if (selected_treatment_temp.action == 'missing') {
            self_var.perform_missing_action(full_mouth_teeth_temp);
        }
        if (full_mouth) {
            // var panned_text = $('#planned').text().trim();
            var panned_text = document.getElementById('planned').textContent.trim()
            var status_to_define_temp = panned_text;
            
            // var completed_text = $('#completed').text().trim();
            var completed_text = document.getElementById('completed').textContent.trim()

            // var inprogress_text = $('#in_progress').text().trim();
            var inprogress_text = document.getElementById('in_progress').textContent.trim()

            var status_defined = status_to_define_temp.toLowerCase();
            if (status_to_define){
                
                if(status_to_define == 'completed'){
                    status_to_define_temp = completed_text;
                }else if(status_to_define == 'in_progress'){
                    status_to_define_temp = inprogress_text;
                }else if(status_to_define == 'planned'){
                    status_to_define_temp = panned_text;
                }
            }
            //status_to_define_temp = status_to_define.substr(0, 1).toUpperCase() + status_to_define.substr(1);
            var today = new Date();
            if (created_date) {
                today = created_date;
                
            }
            var table_str = '';
            this.get_treatment_charge(selected_treatment_temp.treatment_id).then(function(t_charge) {
                 
                if (!t_charge) {
                    t_charge = '0.0';
                }
                operation_id += 1;
                
                var total_teeth = '';
                var surf_list = new Array();
                var name_list = new Array();

                // for(var each_full_mouth_teeth_temp in full_mouth_teeth_temp){
                //     total_teeth += '_' + each_full_mouth_teeth_temp;
                //     surf_list.push('view_' + each_full_mouth_teeth_temp + '_center');
                //     surf_list.push('view_' + each_full_mouth_teeth_temp + '_right');
                //     surf_list.push('view_' + each_full_mouth_teeth_temp + '_left');
                //     surf_list.push('view_' + each_full_mouth_teeth_temp + '_top');
                //     surf_list.push('view_' + each_full_mouth_teeth_temp + '_bottom');
                // }

                full_mouth_teeth_temp.forEach(each_full_mouth_teeth_temp =>{                    
                    total_teeth += '_' + each_full_mouth_teeth_temp;
                    surf_list.push('view_' + each_full_mouth_teeth_temp + '_center');
                    surf_list.push('view_' + each_full_mouth_teeth_temp + '_right');
                    surf_list.push('view_' + each_full_mouth_teeth_temp + '_left');
                    surf_list.push('view_' + each_full_mouth_teeth_temp + '_top');
                    surf_list.push('view_' + each_full_mouth_teeth_temp + '_bottom');
                });                
                self_var.increment_thread(surf_list); 
                               
                total_teeth = total_teeth.substr(1);
                if (other_history)
                    table_str += '<tr class = ' + total_teeth + ' id = operation_' + operation_id + ' style = "display:none">';
                else
                
                table_str += '<tr class = ' + total_teeth + ' id = operation_' + operation_id + '>';
                table_str += '<td id = "date_time_' + operation_id + '">' + today + '</td>';
                table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + selected_treatment_temp.treatment_name+'test1' + '</td>';
                table_str += '<td class = "' + 'all' + '" id = "tooth_' + operation_id + '">' + "-" + '</td>';

                table_str += '<td id = "status_' + operation_id +'" status_name = "'+status_to_define+'">' + status_to_define_temp + '</td>';
                table_str += '<td id = "surface_' + operation_id + '">Full Mouth</td>';

                table_str += '<td id = "dentist_' + operation_id + '">' + user_name + '</td>';
                table_str += '<td id = "amount_' + operation_id + '">' + t_charge + '</td>';
                table_str += '<td class = "progress_table_actions" id = "action_' + operation_id + '">' + selected_treatment_temp.action + '</td>';
                table_str += '<td class = "delete_td" id = "delete_' + operation_id + '">' + '<img src = "/pragtech_dental_management/static/src/img/delete.png" height = "20px" width = "20px"/>' + '</td>';
                table_str += '<td style = "display:none" id = "previous_' + operation_id + '">' + is_prev_record + '</td>';
                table_str += '</tr>';
                var html_table_data = "";  
                var bRowStarted = true; 
                document.querySelectorAll('#operations tbody > tr').forEach(function (row) {                
                    row.querySelectorAll('td').forEach(function (cell) {
                        if (html_table_data.length === 0 || bRowStarted === true) {
                            html_table_data += cell.textContent;
                            bRowStarted = false;
                        } else {
                            html_table_data += " | " + cell.textContent;
                        }
                    });
                
                    html_table_data += "\n";
                    bRowStarted = true;
                });
                var flag = false

                html_table_data.split('\n').forEach(name_treatment => {
                    var description = name_treatment.split('|')[1];
                    var str1 = "" + description;
                    var str2 = "" + selected_treatment_temp.treatment_name;                    
                    var n = str1.trim();
                    var n1 = str2.trim();

                    if (n === n1) {
                        flag = true;
                    }
                });
                if (!flag) {
                    document.getElementById('progres_table').insertAdjacentHTML('beforeend', table_str);
                    
                    document.getElementById('delete_' + operation_id).addEventListener('click', function() {
                        var x = window.confirm("Are you sure you want to delete?");
                        if (x) {
                            update = false;
                            cont = false;
                            var actual_id = parseInt(this.id.substring(7));
                            var tabel = document.getElementById('operations');
                            var tr = document.getElementById('operation_' + actual_id);
                            var tooth = document.getElementById('tooth_' + actual_id);
                            var desc_class = document.getElementById('desc_' + actual_id).className;
                
                            var tooth_id = tr.className.split('_');
                
                            var status = document.getElementById('status_' + actual_id);
                            var status_name = status.getAttribute('status_name');
                
                            if (status_name === 'completed' || status_name === 'in_progress') {
                                alert('Cannot delete');
                            } else {
                                var action = document.getElementById('action_' + actual_id);
                                var action_id = action.innerHTML;
                
                                var surf_list = [];
                                full_mouth_teeth_temp.forEach(function(tooth_id) {
                                    surf_list.push('view_' + tooth_id + '_center');
                                    surf_list.push('view_' + tooth_id + '_right');
                                    surf_list.push('view_' + tooth_id + '_left');
                                    surf_list.push('view_' + tooth_id + '_top');
                                    surf_list.push('view_' + tooth_id + '_bottom');
                                });
                                
                                self_var.decrement_thread(surf_list);
                                self_var.remove_selection_action(tooth_id);
                                if (action_id === 'missing') {
                                    self_var.remove_missing_action(tooth_id);
                                }
                                tr.parentNode.removeChild(tr);
                            }
                        }
                    });
                }
                
                document.querySelectorAll('[id^="operation_"]').forEach(function(row) {
                    row.addEventListener('click', function() {
                        // Remove 'selected_operation' class from all rows
                        document.querySelectorAll('[id^="operation_"]').forEach(function(otherRow) {
                            otherRow.classList.remove('selected_operation');
                        });
                        
                        // Add 'selected_operation' class to the clicked row
                        this.classList.add('selected_operation');
                    });
                });
                

            });
            if (selected_treatment_temp.action == false) {
            }
        }
    }



    put_data(self_var, surfaces, selected_tooth_temp, selected_surface_temp, status_defined, created_date, is_prev_record, other_history,description) {         
        if (!selected_tooth_temp) {
            
            selected_tooth_temp = "-";
        }
        if (description.treatment_name != undefined && selected_treatment.treatment_id != description.treatment_id){
            selected_treatment = description
            

        }

        var selected_treatment_temp = selected_treatment;

        

        if (!selected_treatment_temp.treatment_name){
            selected_treatment_temp=description            
            
        }
       
        var table_str = '';
        user_name = dentist_name
        
        

        var today = new Date();
        if (created_date) {
            today = created_date;
            
            
        }
        var panned_text = document.getElementById('planned').textContent.trim();
        var status_to_use = panned_text;
        var completed_text = document.getElementById('completed').textContent.trim();        
       
        var inprogress_text = document.getElementById('in_progress').textContent.trim();

        if (status_defined)
            if(status_defined == 'completed'){
                status_to_use = completed_text;
            }else if(status_defined == 'in_progress'){
                status_to_use = inprogress_text;
            }else if(status_defined == 'planned'){
                status_to_use = panned_text;
            }
        if (status_to_use == 'planned'){
            status_to_use = panned_text;
        }
        
        this.get_treatment_charge(selected_treatment_temp.treatment_id).then(function(t_charge) {
            if (!t_charge) {
                t_charge = '0.0';
            }
            if (description.amount){
                t_charge = description.amount
            }
            operation_id += 1;
            var found = document.querySelector('.selected_operation');
           
            if (found) {
                found.classList.remove("selected_operation");
            }
            if (other_history)
                table_str += '<tr id = operation_' + operation_id + ' style= "display:none">';
            else
                table_str += '<tr id = operation_' + operation_id + '>';
            table_str += '<td id = "date_time_' + operation_id + '">' + today + '</td>';
            if (description.treatment_name == undefined){
            table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + selected_treatment_temp.treatment_name + '</td>';
                
            }else{
            table_str += '<td class = "' + selected_treatment_temp.treatment_id + '" ' + 'id = "desc_' + operation_id + '">' + description.treatment_name + '</td>';
                  
            }

            if (type == 'palmer') {

                var numbers = parseInt(selected_tooth_temp);
                if (selected_tooth_temp == "-") {
                    numbers = "-";
                }
                switch(numbers) {
                case 1:
                    table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Palmer[1] + '</td>';
                    break;
                case 2:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[2] + '</td>';
                    break;
                case 3:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[3] + '</td>';
                    break;
                case 4:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[4] + '</td>';
                    break;
                case 5:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[5] + '</td>';
                    break;
                case 6:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[6] + '</td>';
                    break;put_data
                case 7:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[7] + '</td>';
                    break;
                case 8:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[8] + '</td>';
                    break;
                case 9:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[9] + '</td>';
                    break;
                case 10:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[10] + '</td>';
                    break;
                case 11:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[11] + '</td>';
                    break;
                case 12:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[12] + '</td>';
                    break;
                case 13:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[13] + '</td>';
                    break;
                case 14:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[14] + '</td>';
                    break;
                case 15:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[15] + '</td>';
                    break;
                case 16:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[16] + '</td>';
                    break;
                case 17:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[17] + '</td>';
                    break;
                case 18:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[18] + '</td>';
                    break;
                case 19:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[19] + '</td>';
                    break;
                case 20:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[20] + '</td>';
                    break;
                case 21:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[21] + '</td>';
                    break;
                case 22:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[22] + '</td>';
                    break;
                case 23:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[23] + '</td>';
                    break;
                case 24:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[24] + '</td>';
                    break;
                case 25:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[25] + '</td>';
                    break;
                case 26:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[26] + '</td>';
                    break;
                case 27:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[27] + '</td>';
                    break;
                case 28:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[28] + '</td>';
                    break;
                case 29:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[29] + '</td>';
                    break;
                case 30:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[30] + '</td>';
                    break;
                case 31:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[31] + '</td>';
                    break;
                case 32:
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + Palmer[32] + '</td>';
                    break;
                case "-":
                    table_str += '<td  class="' + selected_tooth_temp + '"id = "tooth_' + operation_id + '">' + "-" + '</td>';
                    break;

                }
            } else if (type == 'universal') {
                table_str += '<td class = "' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + selected_tooth_temp + '</td>';
            } else if (type == 'iso') {
                var numbers = parseInt(selected_tooth_temp);

                switch(numbers) {
                case 1:
                    table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[1] + '</td>';
                    break;
                case 2:
                    table_str += '<td class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[2] + '</td>';
                    break;
                case 3:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[3] + '</td>';
                    break;
                case 4:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[4] + '</td>';
                    break;
                case 5:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[5] + '</td>';
                    break;
                case 6:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[6] + '</td>';
                    break;
                case 7:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[7] + '</td>';
                    break;
                case 8:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[8] + '</td>';
                    break;
                case 9:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[9] + '</td>';
                    break;
                case 10:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[10] + '</td>';
                    break;
                case 11:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[11] + '</td>';
                    break;
                case 12:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[12] + '</td>';
                    break;
                case 13:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[13] + '</td>';
                    break;
                case 14:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[14] + '</td>';
                    break;
                case 15:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[15] + '</td>';
                    break;
                case 16:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[16] + '</td>';
                    break;
                case 17:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[17] + '</td>';
                    break;
                case 18:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[18] + '</td>';
                    break;
                case 19:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[19] + '</td>';
                    break;
                case 20:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[20] + '</td>';
                    break;
                case 21:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[21] + '</td>';
                    break;
                case 22:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[22] + '</td>';
                    break;
                case 23:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[23] + '</td>';
                    break;
                case 24:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[24] + '</td>';
                    break;
                case 25:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[25] + '</td>';
                    break;
                case 26:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[26] + '</td>';
                    break;
                case 27:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[27] + '</td>';
                    break;
                case 28:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[28] + '</td>';
                    break;
                case 29:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[29] + '</td>';
                    break;
                case 30:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[30] + '</td>';
                    break;
                case 31:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[31] + '</td>';
                    break;
                case 32:
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + Iso[32] + '</td>';
                    break;
                case "-":
                    table_str += '<td  class="' + selected_tooth_temp + '" id = "tooth_' + operation_id + '">' + "-" + '</td>';
                    break;

                }
            }
            table_str += '<td id = "status_' + operation_id +'" status_name = "'+status_defined+'">' + status_to_use + '</td>';
        
            table_str += '<td id = "surface_' + operation_id + '">';
            // surfaces.forEach(eachSurf => {
            //     table_str += eachSurf + ' ';
            // });
            let uniqueSurfaces = new Set(surfaces);
            if (uniqueSurfaces.size < 5) {
                uniqueSurfaces.forEach(eachSurf => {
                    table_str += eachSurf + ' ';
                });
            }
            else {
                table_str += 'Full Tooth';
            }
            self_var.increment_thread(selected_surface_temp);            
            table_str += '<p style="display:none" id="selected_surface_'+operation_id+'">'+ selected_surface_temp+'</p>'
            table_str += '</td>';
            table_str += '<td id = "dentist_' + operation_id + '">' + user_name + '</td>';
            table_str += '<td id = "amount_' + operation_id + '">' + t_charge + '</td>';
            table_str += '<td class = "progress_table_actions" id = "action_' + operation_id + '">' + selected_treatment_temp.action + '</td>';
            table_str += '<td class = "delete_td" id = "delete_' + operation_id + '">' + '<img src = "/pragtech_dental_management/static/src/img/delete.png" height = "20px" width = "20px"/>' + '</td>';
            table_str += '<td style = "display:none" id = "previous_' + operation_id + '">' + is_prev_record + '</td>';
            table_str += '</tr>';

            document.getElementById('progres_table').insertAdjacentHTML('beforeend', table_str);

           // Adding click event listener to the new row to handle row selection
            document.querySelectorAll('[id^="operation_"]').forEach(function(row) {
                row.addEventListener('click', function() {
                    // Remove 'selected_operation' class from all rows
                    document.querySelectorAll('[id^="operation_"]').forEach(function(r) {
                        r.classList.remove('selected_operation');
                    });

                    // Add 'selected_operation' class to the clicked row
                    row.classList.add('selected_operation');
                });
            });
           
            document.getElementById('delete_' + operation_id).addEventListener('click', function() {
                var x = window.confirm("Are you sure you want to delete?");
                if (x) {
                    update = false;
                    cont = false;
                    var actual_id = parseInt(this.id.substring(7));
                    var table = document.getElementById('operations');
                    var tr = document.getElementById('operation_' + actual_id);
                    var tooth = document.getElementById('tooth_' + actual_id);
                    var desc_class = document.getElementById('desc_' + actual_id).className;
                    var tooth_id = tooth ? tooth.className : null;
                    var status = document.getElementById('status_' + actual_id);
                    var status_name = status ? status.getAttribute('status_name') : null;
            
                    if (status_name === 'completed' || status_name === 'in_progress') {
                        alert('Cannot delete');
                    } else {
                        var action = document.getElementById('action_' + actual_id);
                        var action_id = action.innerHTML; {
                        var surface_vals = document.getElementById('surface_' + actual_id).textContent.split(' ');
                        var surf_list = [];
                                    
                        surface_vals.forEach(function(sv) {
                            var elementIds = [
                                'view_' + tooth_id + '_center',
                                'view_' + tooth_id + '_right',
                                'view_' + tooth_id + '_left',
                                'view_' + tooth_id + '_top',
                                'view_' + tooth_id + '_bottom'
                            ];
                        
                            elementIds.forEach(function(id) {
                                var elem = document.getElementById(id);
                                if (elem) {
                                    var classList = elem.getAttribute("class");
                                    if (classList) {
                                        var classArray = classList.split(' ');
                                        if (classArray.length > 1 && classArray[1] === sv) {
                                            surf_list.push(id);                                            
                                        }
                                    }
                                } else {
                                    console.warn('Element with ID ' + id + ' not found.');
                                }
                            });
                        });
            
                        self_var.decrement_thread(surf_list);
                    }
                        if (action_id === 'missing') {
                            var toothElem = document.getElementById(tooth_id);
                            if (toothElem) {
                                toothElem.style.visibility = "visible";
                                toothElem.className = 'teeth';
                            }
                            
                            var views = ['_top', '_left', '_bottom', '_right', '_center'];
                            views.forEach(function(view) {
                                var elem = document.getElementById('view_' + tooth_id + view);
                                if (elem) {
                                    elem.style.visibility = 'visible';
                                    elem.setAttribute('fill', 'white');
                                }
                            });
                        } else {
                            ['_bottom', '_right', '_center', '_left', '_top'].forEach(function(view) {
                                var elem = document.getElementById('view_' + tooth_id + view);
                                if (elem) { // Check if elem is not null
                                    var classList = elem.getAttribute("class");
                                    if (classList) { // Check if classList is not null
                                        var classArray = classList.split(' ');
                                        if (classArray.length > 3) { // Ensure there are enough elements in the array
                                            var elem1 = classArray[3];
                                            if (parseInt(elem1) === 0) {
                                                elem.setAttribute('fill', 'white');
                                            }
                                        }
                                    }
                                }
                                });
                        }
            
                        if (tr) {
                            tr.parentNode.removeChild(tr);
                        }
            
                        for (var index = 0; index < treatment_lines.length; index++) {
                            if (treatment_lines[index].tooth_id === tooth_id) {
                                for (var i2 = 0; i2 < treatment_lines[index].treatments.length; i2++) {
                                    if (treatment_lines[index].treatments[i2].treatment_id === parseInt(desc_class)) {
                                        treatment_lines.splice(index, 1);
                                        operation_id += 1;
                                        var found = document.querySelector('.selected_treatment_temp');
                                        if (found) {
                                            found.classList.remove("selected_treatment_temp");
                                        }
                                        return;
                                    }
                                }
                            }
                        }
                    }
                }
            });
            


        });
    }


    async writePatientHistory(selfVar, res) {
        let isPrevRecordFromWrite = false;
    
        for (const eachOperation of res) {
            const selectedTreatment = {
                'treatmentId': eachOperation['desc']['id'],
                'treatmentName': eachOperation['desc']['name'],
                'action': eachOperation['desc']['action']
            };
    
    
            isPrevRecordFromWrite = false;
    
            if (eachOperation['status'] === 'completed') {
                isPrevRecordFromWrite = true;
            }
            if (eachOperation['status'] === 'in_progress') {
                eachOperation['status'] = 'in_progress';
            }
    
            if (eachOperation['tooth_id']) {
                await selfVar.put_data(selfVar, eachOperation['surface'].split(' '), eachOperation['tooth_id'], false, eachOperation['status'], eachOperation['created_date'], isPrevRecordFromWrite, eachOperation['other_history']);
            } else {
                await selfVar.put_data_full_mouth(selfVar, eachOperation.multiple_teeth, 1, selectedTreatment, eachOperation['status'], eachOperation['created_date'], isPrevRecordFromWrite, eachOperation['other_history']);
            }
        }
    
        selectedTreatment = '';
    }

    async execute_create(attrs, selfVar, selected_surface_temp) {
    
        if (!selected_surface_temp) {
            selected_surface_temp = selected_surface;
        }
    
        // const activeId = this.context.active_id;
        // const data = await this.orm.call('medical.patient', 'get_data', [this.context.active_id, activeId], {});
        // const dentist_id = data.dentist_id;
        // const dentist_name = data.dentist_name;
    
    
        const tooth_present = this.checkIfToothPresent(selected_tooth);
    
        var record = new Array();			
			record['treatments'] = new Array();
			record['tooth_id'] = selected_tooth;
			record['dentist'] = dentist_id;
        
        
    
        var surfaces = new Array();
        var selected_area = new Array();
    
        selected_surface_temp.forEach(function(each_surface) {
    
            selected_area.push(each_surface);
    
            const element = document.getElementById(each_surface);
            var surface = element.getAttribute("class").split(" ")[1];
            surfaces.push(surface);
            
        });
    
        const d = {
            treatment_id: selected_treatment['treatment_id'],
            vals: surfaces,
        };
        
    
        const selected_tooth_temp = selected_tooth;
        
    
        if (attrs) {
            if (!tooth_present) {
                record['treatments'].push(d);
                treatment_lines.push(record);
                
    
                this.put_data(selfVar, surfaces, selected_tooth_temp, selected_surface_temp, 'planned', false, false, false, false);                
            } else {
                
                let treatment_present = 0;
                for (let i = 0; i < treatment_lines.length; i++) {
                    if (treatment_lines[i]['tooth_id'] == parseInt(selected_tooth_temp)) {
                        for (let each_trts = 0; each_trts < treatment_lines[i]['treatments'].length; each_trts++) {
                            if (treatment_lines[i]['treatments'][each_trts].treatment_id == selected_treatment['treatment_id']) {
                                treatment_present = 1;
                                break;
                            }
                        }
                        if (!treatment_present) {
                            treatment_lines[i]['treatments'].push(d);
                            this.put_data(selfVar, surfaces, selected_tooth_temp, selected_surface_temp, false, false, false, false, false);
                        }
                    }
                }
            }
        } else {
            
            if (!tooth_present) {
                record['treatments'].push(d);
                treatment_lines.push(record);
                surfaces.length = 0;
                this.put_data(selfVar, surfaces, selected_tooth_temp, false, false, false, false, false);
            }
        }
    }
       
    
}

DentalChartAction.template = "pragtech_dental_management.DentalAction";

registry
    .category("actions")
    .add("dental_chart", DentalChartAction, { force: true });
