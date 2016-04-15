(function($) {

   var rules = {
      required: {
         selector: '.required',
         rule: function($el) {
            return ($el.attr('type') != 'checkbox' && $el.val().length > 0) || $el.attr('checked');
         }
      },
      notdefault: {
         selector: '.notdefault',
         rule: function($el) {
            return $el.val() != $el[0].defaultValue;
         }
      },
      email: { selector: '.email', rule: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i },
      date: { selector: '.date', rule: /^[0-3]?[0-9]\/[0123]?[0-9]\/[12][09][0-9][0-9]$/ },
      numeric: { selector: '.numeric', rule: /^[\d]*(\.[\d]{1,})?$/ },
      url: { selector: '.url', rule: /(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?/ }
   };


   var methods = {
      init: function(options) {

         var settings = {
            'refocus':         true,
            'invalidClass':    'alert',
            'invalidSelector':    'label[for=<<id>>]',
            'invalidCallback':    null,
            'validCallback':    null,
            'smother':          false
         };

         if(options) {
            $.extend(settings, options);
         }

         return this.each(function() {

            var $this = $(this);

            $this.bind('submit.legit', function(e) {

               if(settings.smother) {
                  e.preventDefault();
               }

               var feedback = '', focus = false, tmpSelector;

               $this.find('input[type="password"]:enabled, input[type="file"]:enabled, input[type="text"]:enabled, input[type="checkbox"]:enabled, select:enabled, textarea:enabled').each(function() {

                  var $el = $(this), valid = true;

                  for(var i in rules) {

                     if($el.is(rules[i].selector)) {

                        if(i != 'required' && $el.val().length == 0) {
                           //the field is empty and only the required rule tests empty fields
                           continue;
                        }

                        if(typeof rules[i].rule.test == 'function') {
                           if(!rules[i].rule.test($el.val())) {
                              valid = false;
                           }
                        }
                        else if(typeof rules[i].rule == 'function' && !rules[i].rule($el)) {
                           valid = false;
                        }

                     }

                  }

                  tmpSelector = false;
                  if(settings.invalidSelector) {
                     tmpSelector = settings.invalidSelector.replace(/<<id>>/g, $el.attr('id')).replace(/<<name>>/g, $el.attr('name'));
                  }

                  if(!valid) {

                     if(settings.invalidClass) {
                        if(tmpSelector) {
                           console.log(tmpSelector);
                           console.log($(tmpSelector));
                           $(tmpSelector).addClass(settings.invalidClass);
                        }
                        else {
                           $el.addClass(settings.invalidClass);
                        }
                     }

                     feedback += $el.attr('title') + "\n";
                     if(!focus) focus = $el;
                  }
                  else {

                     if(settings.invalidClass) {
                        if(tmpSelector) {
                           $(tmpSelector).removeClass(settings.invalidClass);
                        }
                        else {
                           $el.removeClass(settings.invalidClass);
                        }
                     }
                  }

               });

               if(feedback.length > 0) {

                  if(settings.refocus) focus.focus();

                  if(typeof settings.invalidCallback == 'function') {
                     return settings.invalidCallback(feedback);
                  }
                  else {
                     alert(feedback);
                     return false;
                  }
               }

               if(typeof settings.validCallback == 'function') {
                  return settings.validCallback(feedback);
               }
               else {
                  return true;
               }
            });
         });
      }, //init

      destroy: function() {

         this.unbind('.legit');

         return this;
      }, //destroy

      addRule: function(name, rule) {

         rules[name] = rule;

         return this;
      }
   };

   $.fn.legit = function(method) {
      if(methods[method]) {
         return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      }
      else if(typeof method === 'object' || !method) {
         return methods.init.apply(this, arguments);
      }
      else {
         $.error('Method ' + method + ' does not exist on jQuery.legit');
      }
   }

})(jQuery);
