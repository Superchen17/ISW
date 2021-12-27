import React from 'react';
import {Menu, Layout, Select} from 'antd';
import {Divider} from 'antd';

import {Table, TableBody, TableCell, TableHead, TableRow} from "@material-ui/core";
import {Button, IconButton} from '@material-ui/core';
import {NavigateNext, NavigateBefore} from '@material-ui/icons'
import {CircularProgress} from '@material-ui/core';

import socket from '../../socket';

import 'antd/dist/antd.css';

export class PageISW extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            selected_data: null,

            images_distorted: null,
            images_distorted_index: 1,
            image_before: null,
            image_groundtruth: null,
            image_recv: null,

            ssim: null,
            psnr: null,
            mse: null,

            datasets: null, 
        }
    }

    componentDidMount(){
        //* event receivers
        socket.on('r_restore', (r) => {
            if(r === 'processing'){
                this.setState({
                    image_recv: 'processing',
                })
                return;
            }
            var str = String.fromCharCode.apply(null, new Uint8Array(r.restored));
            this.setState({
                image_recv: "data:image/png;base64," + btoa(str),
                ssim: r.ssim,
                psnr: r.psnr,
                mse: r.mse
            });
        });
        socket.on('r_get_datasets', (d) => {
            this.setState({datasets: d});
        });
        socket.on('r_get_preview_isw', (r) => {
            var bit_str1 = String.fromCharCode.apply(null, new Uint8Array(r.distorted[0])); 
            bit_str1 = "data:image/png;base64," + btoa(bit_str1);

            var bit_str2;
            if(r.groundtruth === 'na'){
                bit_str2 = r.groundtruth;
            }
            else{
                bit_str2 = String.fromCharCode.apply(null, new Uint8Array(r.groundtruth));
                bit_str2 = "data:image/png;base64," + btoa(bit_str2);
            }

            this.setState({
                image_before: bit_str1,
                image_groundtruth: bit_str2,
                images_distorted: r.distorted,
                images_distorted_index: 1,
            })
        });

        //* event emitters
        socket.emit('get_datasets');
    }

    get_preview = (event) => {
        const dataset = event.key;
        socket.emit('get_preview_isw', dataset);
        this.setState({
            selected_data: dataset, 
            image_recv: null, 
            ssim: null,
            psnr: null,
            mse: null
        });
    }

    navi_distorted = (event) => {
        var id = event.currentTarget.id;
        var index;

        if(id === '+'){
            (this.state.images_distorted.length !== this.state.images_distorted_index)
            ? index = this.state.images_distorted_index + 1
            : index = 1
        }
        else if(id === '-'){
            (this.state.images_distorted_index !== 1)
            ? index = this.state.images_distorted_index - 1
            : index = this.state.images_distorted.length
        }

        var bit_str = String.fromCharCode.apply(null, new Uint8Array(this.state.images_distorted[index-1])); 
        bit_str = "data:image/png;base64," + btoa(bit_str);

        this.setState({
            images_distorted_index: index,
            image_before: bit_str
        })
        console.log(this.state.images_distorted_index);
    }

    submit_isw = () => {
        if(this.state.selected_data === null){
            alert('Select a dataset first');
            return;
        }
        socket.emit('restore', {
            dataset: this.state.selected_data,
       });
    }

    render(){
        if(this.state.datasets === null){
            return(
                <div style={{position: 'absolute', left: '50%', top: '50%'}}>
                    <CircularProgress />
                </div>
            );       
        }

        const isw_menu = (
            <div>
                <div style={{textAlign: 'center', marginTop: '25px'}}>
                    <h3>Available Datasets</h3>
                </div>
                <Divider />
                <Menu mode="inline" title='Available Datasets'>
                    {
                        this.state.datasets.map((dataset, index) => (
                            <Menu.Item onClick={this.get_preview} key={dataset}>{dataset}</Menu.Item>
                        ))
                    }
                </Menu>
            </div>
        );  

        const div_style = (color) => {
            return {
                width: '33%', 
                height: '100%',
                backgroundColor: color, 
                position: 'relative', 
                float: 'left',
                padding: '5px',
                textAlign: 'center',
            };
        }

        return(
            <Layout>
                <Layout.Sider width='256' theme='light'>
                    {isw_menu}
                </Layout.Sider>
                <Layout.Content>
                    <div style={{flexDirection: 'vertical', height: '450px', textAlign: 'center'}}>
                        <div style={div_style('#E0E0E0')}>
                            <h3>Distorted Sample</h3>
                            {
                                this.state.image_before && 
                                <div>
                                    <img src={this.state.image_before} style={{width: '100%'}}/>
                                    <br/>
                                    <IconButton id='-' size='small'onClick={this.navi_distorted}>
                                        <NavigateBefore/>
                                    </IconButton>
                                    Frame {this.state.images_distorted_index} of {this.state.images_distorted.length}
                                    <IconButton id='+' size='small' onClick={this.navi_distorted}>
                                        <NavigateNext/>
                                    </IconButton>
                                </div> 
                            }
                        </div>
                        <div style={div_style('white')}>
                            <h3>Ground Truth</h3>
                            {
                                this.state.image_groundtruth && (
                                   this.state.image_groundtruth === 'na'
                                   ? <h3>Unavailable</h3>
                                   :<img src={this.state.image_groundtruth} style={{width: '100%'}}/>
                               )
                            }
                        </div>
                        <div style={div_style('#E0E0E0')}>
                            <h3>Restored Image</h3>
                            {
                                this.state.image_recv && (
                                    this.state.image_recv === 'processing'
                                    ? <CircularProgress style={{position: 'absolute', top: '50%', left: '50%'}}/>
                                    : <img src={this.state.image_recv} style={{width: '100%'}}/>
                               )
                            }
                        </div>
                    </div>

                    <br/>
                    <div style={{textAlign: 'center'}}>
                        <Select 
                            placeholder="Select an algorithm" 
                            style={{ width: 250, marginRight: '50px'}} 
                        >
                            <Select.Option value="proposed">Hierarchical Fusion (Proposed)</Select.Option>
                            <Select.Option value="shift-map">Shift Map (Halder <i>et al.</i>)</Select.Option>
                        </Select>
                        <button style={{marginLeft: '50px'}} onClick={this.submit_isw}>
                            Run Restoration
                        </button>
                    </div>

                    <Divider orientation='left'>Analysis</Divider>

                    <Table style={{width: 500, margin: 'auto'}} size='small'>
                        <TableHead>
                            <TableRow>
                                <TableCell><b>Metric</b></TableCell>
                                <TableCell><b>Value</b></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <TableCell>Structural Similarity</TableCell>
                                <TableCell>{this.state.ssim}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Peak Signal-to-Noise Ratio</TableCell>
                                <TableCell>{this.state.psnr}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Mean Square Error</TableCell>
                                <TableCell>{this.state.mse}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </Layout.Content>
            </Layout>
        );
    }
}
