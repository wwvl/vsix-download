import type { ButtonProps, DrawerProps, ModalProps, SlideoverProps } from '@nuxt/ui'

export type HeaderMode = 'modal' | 'slideover' | 'drawer'

export type HeaderMenu<T extends HeaderMode>
  = T extends 'modal' ? ModalProps
    : T extends 'slideover' ? SlideoverProps
      : T extends 'drawer' ? DrawerProps
        : never

export interface HeaderProps<T extends HeaderMode> {
  /**
   * The element or component this component should render as.
   * @defaultValue 'header'
   */
  as?: any
  title?: string
  to?: string
  /**
   * The mode of the header menu.
   * @defaultValue 'modal'
   */
  mode?: T
  /**
   * The props for the header menu component.
   */
  menu?: HeaderMenu<T>
  /**
   * Customize the toggle button to open the header menu displayed when the `content` slot is used.
   * `{ color: 'neutral', variant: 'ghost' }`{lang="ts-type"}
   */
  toggle?: ButtonProps
  /**
   * The side to render the toggle button on.
   * @defaultValue 'right'
   */
  toggleSide?: 'left' | 'right'
  class?: any
}

export interface HeaderSlots {
  title: (props?: Record<string, unknown>) => any
  left: (props?: Record<string, unknown>) => any
  default: (props?: Record<string, unknown>) => any
  right: (props?: Record<string, unknown>) => any
  toggle: (props?: Record<string, unknown>) => any
  top: (props?: Record<string, unknown>) => any
  bottom: (props?: Record<string, unknown>) => any
  content: (props?: Record<string, unknown>) => any
}
