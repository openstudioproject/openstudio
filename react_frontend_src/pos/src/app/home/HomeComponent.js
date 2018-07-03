import React, { Component } from "react"
import PageTemplate from "../../components/PageTemplate"

class homeComponent extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    setLoaderStatus(status) {
        this.props.setLoaderStatus(status)
    }

    setLoaderMessage(message) {
        this.props.setLoaderMessage(message)
    }

    componentWillMount() {
        this.setLoaderStatus('loading')
    }

    componentDidMount() {
        setTimeout(() => this.setLoaderMessage('phase 1'), 0)
        setTimeout(() => this.setLoaderMessage('phase 2'), 1000)
        //setTimeout(() => this.setLoaderMessage('phase 3'), 2500)
        // ready...
        setTimeout(() => this.setLoaderStatus('ready'), 1000)
        setTimeout(() => this.setLoaderMessage('Loading done!'), 1500)
        
    }

    render() {
        return (this.props.app.status === 'loading') ?
            <div>Loading... <br /> {this.props.app.message} </div> :
            <PageTemplate>
            <section className="Welcome">
                <div>Welcome page</div>
                <div>{this.props.app.status}</div>
                <div>{this.props.app.message}</div>
            </section>
            </PageTemplate>
    }
}

export default homeComponent
