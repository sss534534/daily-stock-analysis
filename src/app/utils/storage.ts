import { Position } from '../types/stock';

const STORAGE_KEY = 'stock_positions';

export const getPositions = (): Position[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load positions:', error);
    return [];
  }
};

export const savePositions = (positions: Position[]): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
  } catch (error) {
    console.error('Failed to save positions:', error);
  }
};

export const addPosition = (position: Omit<Position, 'id'>): Position => {
  const positions = getPositions();
  const newPosition: Position = {
    ...position,
    id: Date.now().toString(),
  };
  positions.push(newPosition);
  savePositions(positions);
  return newPosition;
};

export const updatePosition = (id: string, updates: Partial<Position>): void => {
  const positions = getPositions();
  const index = positions.findIndex(p => p.id === id);
  if (index !== -1) {
    positions[index] = { ...positions[index], ...updates };
    savePositions(positions);
  }
};

export const deletePosition = (id: string): void => {
  const positions = getPositions();
  const filtered = positions.filter(p => p.id !== id);
  savePositions(filtered);
};

export const calculatePositionMetrics = (
  position: Position,
  currentPrice: number
): Position => {
  const cost = position.shares * position.buyPrice;
  const totalValue = position.shares * currentPrice;
  const profit = totalValue - cost;
  const profitPercent = (profit / cost) * 100;

  return {
    ...position,
    currentPrice,
    cost,
    totalValue,
    profit,
    profitPercent,
  };
};
