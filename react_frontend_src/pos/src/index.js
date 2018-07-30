import React from 'react'
import ReactDOM from 'react-dom'
import { connect, Provider } from 'react-redux'
import { addLocaleData } from 'react-intl'
import storeFactory from './store'
import en from 'react-intl/locale-data/en'
import App from './app/AppContainer'
import ConnectedIntlProvider from './ConnectedIntlProvider'

const store = storeFactory()
console.log(store.getState())

// addLocaleData([...en, ...nl]) for example to add Dutch
addLocaleData([...en])

ReactDOM.render(
  <Provider store={store}>
      <ConnectedIntlProvider>
        <App />
      </ConnectedIntlProvider>
  </Provider>,
  document.getElementById("app")
)