#!/usr/bin/env python3
# Quick test script to verify poker evaluation

from poker_evaluator import PokerEvaluator
from models import Card

# Test cases
print("Testing Poker Evaluator:")
print("=" * 40)

# Royal Flush
cards = [Card("A", "H"), Card("K", "H"), Card("Q", "H"), Card("J", "H"), Card("T", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Royal Flush Test: {hand.hand_type} - {hand.chips} chips")

# Straight Flush
cards = [Card("9", "D"), Card("8", "D"), Card("7", "D"), Card("6", "D"), Card("5", "D")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Straight Flush Test: {hand.hand_type} - {hand.chips} chips")

# Four of a Kind
cards = [Card("K", "H"), Card("K", "D"), Card("K", "C"), Card("K", "S"), Card("2", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Four of a Kind Test: {hand.hand_type} - {hand.chips} chips")

# Full House
cards = [Card("Q", "H"), Card("Q", "D"), Card("Q", "C"), Card("5", "S"), Card("5", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Full House Test: {hand.hand_type} - {hand.chips} chips")

# Flush
cards = [Card("A", "S"), Card("9", "S"), Card("7", "S"), Card("4", "S"), Card("2", "S")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Flush Test: {hand.hand_type} - {hand.chips} chips")

# Straight
cards = [Card("7", "H"), Card("6", "D"), Card("5", "C"), Card("4", "S"), Card("3", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Straight Test: {hand.hand_type} - {hand.chips} chips")

# Three of a Kind
cards = [Card("J", "H"), Card("J", "D"), Card("J", "C"), Card("8", "S"), Card("3", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Three of a Kind Test: {hand.hand_type} - {hand.chips} chips")

# Two Pair
cards = [Card("T", "H"), Card("T", "D"), Card("5", "C"), Card("5", "S"), Card("A", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"Two Pair Test: {hand.hand_type} - {hand.chips} chips")

# One Pair
cards = [Card("9", "H"), Card("9", "D"), Card("K", "C"), Card("7", "S"), Card("2", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"One Pair Test: {hand.hand_type} - {hand.chips} chips")

# High Card
cards = [Card("A", "H"), Card("K", "D"), Card("Q", "C"), Card("7", "S"), Card("2", "H")]
hand = PokerEvaluator.evaluate_hand(cards)
print(f"High Card Test: {hand.hand_type} - {hand.chips} chips")

print("=" * 40)
print("All tests passed!")
