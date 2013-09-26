// Copyright (c) The TwistedFTW Team
// See LICENSE for details.

var app = angular.module('article', []);

app.config(function($routeProvider, $locationProvider) {
  $routeProvider
  .when('/:category/:name', {
    templateUrl: function(params) {
      return 'articles/' + params.category + '/' + params.name + '.html';
    },
    controller: 'ArticleCtrl'
  })
  .otherwise({
    redirectTo: '/'
  });
  $locationProvider
  .html5Mode(false)
  .hashPrefix('!');
});

// XXX copied from mainapp.js
app.factory('ArticleIndex', function($http) {
  return $http.get('article_index.json')
  .then(function(d) {
    return d.data;
  });
});

app.filter('stripCopyright', function() {
  return function(x) {
    return x.replace('# Copyright (c) The TwistedFTW Team\n' +
                     '# See LICENSE for details.\n', '');
  }
});

app.factory('Includer', function($q, $http, $templateCache, $filter) {
  this.get = function(url) {
    var data = $templateCache.get(url);
    var d = $q.defer();
    if (data) {
      d.resolve(data);
    } else {
      $http.get(url)
        .success(function(data) {
          var stripped_data = $filter('stripCopyright')(data);
          $templateCache.put(url, stripped_data);
          d.resolve(stripped_data);
        })
        .error(function(err) {
          d.resolve('ERROR, ERROR loading: ' + url);
        });
    }
    return d.promise;
  }
  return this;
})

app.directive('include', function(Includer) {
  return {
    restrict: 'A',
    link: function(scope, element, attrs) {
      element.innerHTML = 'foo';
      Includer.get(attrs.include).then(function(html) {
        element.text(html);
        element.removeClass('prettyprinted');
        PR.prettyPrint();
      })
    }
  }
});


app.factory('ViewState', function($rootScope, $location, ArticleIndex) {
  this.state = {
    index: null,
    path: $location.path(),
    current_section: {},
    current_article: {},
    current_article_name: ''
  };

  ArticleIndex.then(function(d) {
    this.state.index = d;
  }.bind(this));

  this.refresh = function() {
    if (this.state.index == null) {
      return;
    }
    this.state.path = $location.path();
    var parts = this.state.path.split('/');
    this.state.current_section = this.state.index[parts[1]];
    this.state.current_article_name = parts[2];
    // There must be a better way
    if (this.state.current_section !== undefined) {
      this.state.current_section['articles'].forEach(function(article) {
        if (article.name == parts[2]) {
          this.state.current_article = article;
        }
      }.bind(this));
    }
  };

  $rootScope.$watch(function() {
    return $location.path();
  }, function() {
    this.refresh();
  }.bind(this));

  $rootScope.$watch(function() {
    return this.state.index;
  }.bind(this), function() {
    this.refresh();
  }.bind(this), true);

  return this;
});

app.controller('ArticleCtrl', function($scope, $route, $routeParams) {
  PR.prettyPrint();
  $scope.pretty = function() {
    PR.prettyPrint();
  }
})

app.controller('NavbarCtrl', function($scope, ViewState) {
  $scope.refreshState = function() {
    $scope.path = ViewState.state.path;
    $scope.current_section = ViewState.state.current_section;
    $scope.current_article_name = ViewState.state.current_article_name;
    $scope.current_article = ViewState.state.current_article;
    $scope.index = ViewState.state.index;
  };
  $scope.refreshState();

  $scope.$watch(function() {
    return ViewState.state;
  }, $scope.refreshState, true);
})