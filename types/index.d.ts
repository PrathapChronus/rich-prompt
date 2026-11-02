export type Settings = {
  lists: boolean
  indent: boolean
  pairs: boolean
  capitalize: boolean
  capitalizeI: boolean
  spaceAfterPunct: boolean
  doubleSpacePeriod: boolean
  trimSpaceBeforePunct: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'rich-prompt': { settings: Shaped<Settings> }
  }
}
