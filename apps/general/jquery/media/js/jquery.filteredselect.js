// Copyright (c) 2009, Jurie-Jan Botha
//
// This file is part of the 'jquery' Django application.
//
// 'jquery' is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// 'jquery' is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with the 'jquery' application. If not, see
// <http://www.gnu.org/licenses/>.


(function($) {

$.fn.filteredselect = function(target, options) {
    settings = $.extend({}, options);

    return this.each(function() {
        target = $(target);
        select = $(this);
        value = select.val();
        select.empty();
        select.append('<option selected="selected">---------</option>');
        select.append(target.children(':selected').clone());
        select.val(value);

        target.change(function() {
            value = select.val();
            select.empty();
            select.append('<option selected="selected">---------</option>');
            selected = $(this).children(':selected');
            $(this).children(':selected').each(function() {
                select.append($(this).clone());
            });
            select.val(value);
        });
    });
};

})(jQuery);
