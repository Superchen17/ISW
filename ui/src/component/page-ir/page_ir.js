import React from 'react';
import {Menu, Layout, Select} from 'antd';
import {Slider, InputNumber} from 'antd';
import {Divider} from 'antd';

import {Table, TableBody, TableCell, TableHead, TableRow} from "@material-ui/core";
import {CircularProgress} from '@material-ui/core';

import socket from '../../socket';

import 'antd/dist/antd.css';

export class PageIR extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            selected_data: null,

            //* images 
            image_before: null,
            image_after: null,
            image_recv: null,

            //* algorithm parameters
            algorithm: null, //* ['horn-schunck', 'farneback']
            alpha: 15,

            //* returned metrics
            mse: null,

            datasets: null,
        };
    }

    componentDidMount(){
        //* event receivers
        socket.on('r_register', (r) => {
            if(r === 'processing'){
                this.setState({
                    image_recv: 'processing',
                })
                return;
            }
            var str = String.fromCharCode.apply(null, new Uint8Array(r.registered));
            this.setState({
                image_recv: "data:image/png;base64," + btoa(str),
                mse: r.mse
            });
        });
        socket.on('r_get_datasets', (d) => {
            this.setState({datasets: d});
        });
        socket.on('r_get_preview_ir', (imgs) => {
            var str1 = String.fromCharCode.apply(null, new Uint8Array(imgs.before));
            var str2 = String.fromCharCode.apply(null, new Uint8Array(imgs.after));
            this.setState({
                image_before: "data:image/png;base64," + btoa(str1),
                image_after: "data:image/png;base64," + btoa(str2),
            });
        })

        //* event emitters
        socket.emit('get_datasets');
    }

    get_preview = (event) => {
        const dataset = event.key;
        socket.emit('get_preview_ir', dataset);
        this.setState({
            selected_data: dataset, 
            image_recv: null,
            mse: null
        });
    }

    submit_ir = () => {
        if(this.state.algorithm === null){
            alert('Select an algorithm first');
            return;
        }
        if(this.state.selected_data === null){
            alert('Select a dataset first');
            return;
        }
        socket.emit('register', {
            dataset: this.state.selected_data,
            algorithm: this.state.algorithm,
            alpha: this.state.alpha
        });
    }

    set_algorithm = (value) => {
        this.setState({
            algorithm: value,
            image_recv: null,
        });
    }

    set_alpha = (value) => {
        if(isNaN(value)){
            return;
        }
        this.setState({alpha: value});
    }

    render(){
        if(this.state.datasets === null){
            return(
                <div
                    style={{
                        position: 'absolute',
                        left: '50%',
                        top: '50%',
                    }}
                >
                    <CircularProgress />
                </div>
            );       
        }

        const ir_menu = (
            <div>
                <div style={{textAlign: 'center', marginTop: '25px'}}>
                    <h3>Available Datasets</h3>
                </div>
                <Divider />
                <Menu mode="inline" title='Available Datasets'>
                    {
                        this.state.datasets.map((dataset, index) => (
                            <Menu.Item onClick={this.get_preview} key={dataset}>
                                {dataset}
                            </Menu.Item>
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

        const params_hs = (
            <Table style={{width: 1000, margin: 'auto'}} size='small'>
                <TableHead>
                    <TableRow>
                        <TableCell width='20%'><b>Parameter</b></TableCell>
                        <TableCell width='40%'><b>Description</b></TableCell>
                        <TableCell width='30%'><b>Value</b></TableCell>
                        <TableCell width='10%'></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>Smoothness Penalty (&alpha;)</TableCell>
                        <TableCell>The greater the value, the more coherent the result</TableCell>
                        <TableCell>
                            <Slider 
                                style={{width: '200px', backgroundColor: 'black'}} 
                                min={1} 
                                max={40} 
                                value={this.state.alpha}
                                onChange={this.set_alpha}
                            />
                        </TableCell>
                        <TableCell>
                            <InputNumber 
                                min={1} 
                                max={40} 
                                value={this.state.alpha}
                                onChange={this.set_alpha}
                            />
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        );

        return(
            <Layout>
                <Layout.Sider 
                    width='256' 
                    theme='light'
                >
                    {ir_menu}
                </Layout.Sider>
                <Layout.Content>
                    <div style={{flexDirection: 'vertical', height: '450px'}}>
                        <div style={div_style('#E0E0E0')}>
                            <h3>Moving</h3>
                            {
                               this.state.image_before && 
                               <img src={this.state.image_before} style={{width: '100%'}}/>
                            }
                        </div>
                        <div style={div_style('white')}>
                            <h3>Reference</h3>
                            {
                               this.state.image_after && 
                               <img src={this.state.image_after} style={{width: '100%'}}/> 
                            }
                        </div>
                        <div style={div_style('#E0E0E0')}>
                            <h3>Registered</h3>
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
                            style={{ width: 200, margin: 'auto'}} 
                            onChange={this.set_algorithm}
                        >
                            <Select.Option value="horn-schunck">Horn-Schunck</Select.Option>
                            <Select.Option value="farneback">Farneback</Select.Option>
                        </Select>
                    </div>

                    <br/>
                    {
                        this.state.algorithm === 'horn-schunck' &&
                        params_hs
                    }

                    <br/>
                    {
                        this.state.algorithm !== null && (
                            <div style={{textAlign: 'center'}}>
                                <button onClick={this.submit_ir}>
                                    Run Image Registration
                                </button>
                            </div>
                        )
                    }
                    
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
                                <TableCell>Mean Square Error</TableCell>
                                <TableCell>{this.state.mse}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>

                    <br/>
                </Layout.Content>
            </Layout>
        );
    }
}
