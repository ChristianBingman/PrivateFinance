$(document).ready(function() {
  const totalSections = 20;
  let show_complex = false

  function showSection(index) {
    $(`#id_memo_${index}`).removeAttr('hidden');
    $(`#id_account_${index}`).removeAttr('hidden');
    $(`#id_amount_${index}`).removeAttr('hidden');
  }

  function hideSection(index) {
    $(`#id_memo_${index}`).attr('hidden', true);
    $(`#id_account_${index}`).attr('hidden', true);
    $(`#id_amount_${index}`).attr('hidden', true);
  }

  function getVisibleSections() {
    let visible = [];
    for (let i = 1; i <= totalSections; i++) {
      if (!$(`#id_amount_${i}`).is('[hidden]')) {
        visible.push(i);
      }
    }
    return visible;
  }

  function showNextSectionIfNeeded() {
    // If we are doing a simple transaction, don't automatically show
    if (!show_complex) {
      return
    }
    const visible = getVisibleSections();

    const amountFilledCount = visible.reduce((total, val) => {
      if ($(`#id_amount_${val}`).val().trim() !== '') {
        return total + 1;
      }
      return total + 0;
    });

    // If the last two sections are empty, hide the last
    if (amountFilledCount + 1 < visible.length && $(`#id_amount_${visible[visible.length - 1]}`).val().trim() === '') {
      hideSection(visible.length)
    }

    if (amountFilledCount == visible.length && visible.length < totalSections) {
      showSection(visible.length + 1);
    }
  }

  // Handle the show-complex button
  $('#show-complex').on('click', function() {
    if (show_complex) {
      $(`#id_memo_1`).add('hidden', true)
      $(`#id_transaction_group_1`).addClass('inline')
      hideSection(2);
      show_complex = false
    } else {
      $(`#id_memo_1`).removeAttr('hidden')
      $(`#id_transaction_group_1`).removeClass('inline')
      showSection(2);
      show_complex = true
    }
  });

  // Watch for input in any amount field
  for (let i = 1; i <= totalSections; i++) {
    $(`#id_amount_${i}`).on('input', function() {
      showNextSectionIfNeeded();
    });
  }
});
