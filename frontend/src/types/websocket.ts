export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting';

export interface ConnectionAckEvent {
  type: 'connection.ack';
  contentId: string;
}

export interface StateChangeEvent {
  type: 'state.change';
  contentId: string;
  campaignId: string;
  oldState: string;
  newState: string;
  action: string;
  timestamp: string;
}

export type WSInboundEvent = ConnectionAckEvent | StateChangeEvent;

export interface WSSubscriber {
  onEvent: (event: WSInboundEvent) => void;
  onStatusChange: (status: ConnectionStatus) => void;
}
