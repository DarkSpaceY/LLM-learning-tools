class EventBus {
  constructor() {
    this.events = {}
  }

  on(eventName, callback) {
    if (!this.events[eventName]) {
      this.events[eventName] = []
    }
    this.events[eventName].push(callback)
  }

  off(eventName, callback) {
    if (!this.events[eventName]) return
    this.events[eventName] = this.events[eventName].filter(cb => cb !== callback)
  }

  emit(eventName, data) {
    if (!this.events[eventName]) return
    this.events[eventName].forEach(callback => {
      callback(data)
    })
  }
}

export const eventBus = new EventBus()

// 定义事件常量
export const Events = {
  THEME_CHANGE: 'theme_change',
  LANGUAGE_CHANGE: 'language_change',
  SETTINGS_UPDATED: 'settings_updated'
}