"""White-box tests for card deck flow and empty-deck behavior."""

from moneypoly.cards import CardDeck


def test_draw_cycles_and_peek_preserves_order():
    """The deck should cycle deterministically and allow peeking."""
    first = {"description": "First"}
    second = {"description": "Second"}
    deck = CardDeck([first, second])

    assert deck.peek() is first
    assert deck.draw() is first
    assert deck.draw() is second
    assert deck.draw() is first


def test_cards_remaining_and_repr_handle_empty_deck():
    """Empty decks should return safe zero-state values instead of crashing."""
    deck = CardDeck([])

    assert deck.draw() is None
    assert deck.peek() is None
    assert deck.cards_remaining() == 0
    assert repr(deck) == "CardDeck(0 cards, next=empty)"


def test_reshuffle_resets_index(monkeypatch):
    """Reshuffling should reorder the deck and reset the draw pointer."""
    cards = [{"description": "A"}, {"description": "B"}, {"description": "C"}]
    deck = CardDeck(cards)

    def reverse_in_place(items):
        items.reverse()

    monkeypatch.setattr("moneypoly.cards.random.shuffle", reverse_in_place)
    deck.draw()

    deck.reshuffle()

    assert deck.index == 0
    assert deck.draw()["description"] == "C"
