import React from 'react'
import ReactDOM from 'react-dom'
import { connect, Provider } from 'react-redux'
import { addLocaleData } from 'react-intl'
import storeFactory from './store'
import en from 'react-intl/locale-data/en'
import App from './app/App'
import { appOperations } from './app/duck'
import ConnectedIntlProvider from './ConnectedIntlProvider'

const store = storeFactory()
console.log(store.getState())

const mapStateToProps = state => 
    ({
        app_state: state.root.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoaded(loaded) {
            dispatch(appOperations.setLoaded(loaded))
        },
        setLoading(loading) {
            dispatch(appOperations.setLoading(loading))
        },
        setLoadingMessage(message) {
            dispatch(appOperations.setLoadingMessage(message))
        }
    })


const ConnectedApp = connect(
    mapStateToProps,
    mapDispatchToProps
)(App)

// addLocaleData([...en, ...nl]) for example to add Dutch
addLocaleData([...en])

ReactDOM.render(
  <Provider store={store}>
      <ConnectedIntlProvider>
        <ConnectedApp />
      </ConnectedIntlProvider>
  </Provider>,
  document.getElementById("app")
)