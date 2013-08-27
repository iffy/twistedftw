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

app.factory('Includer', function($q, $http, $templateCache) {
  this.get = function(url) {
    var data = $templateCache.get(url);
    var d = $q.defer();
    if (data) {
      d.resolve(data);
    } else {
      $http.get(url)
        .success(function(data) {
          $templateCache.put(url, data);
          d.resolve(data);
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


app.controller('ArticleCtrl', function($scope, $route, $routeParams) {
  PR.prettyPrint();
  $scope.pretty = function() {
    PR.prettyPrint();
  }
})

app.controller('NavbarCtrl', function($scope, $location, ArticleIndex) {
  $scope.path = $location.path();
  $scope.current_section = {};
  $scope.current_article_name = '';
  $scope.current_article = {};
  $scope.index = {};
  ArticleIndex.then(function(d) {
    $scope.index = d;
  });

  $scope.updateCurrents = function() {
    $scope.path = $location.path();
    var parts = $scope.path.split('/');
    $scope.current_section = $scope.index[parts[1]];
    $scope.current_article_name = parts[2];
    // There must be a better way
    if ($scope.current_section !== undefined) {
      $scope.current_section['articles'].forEach(function(article) {
        if (article.name == parts[2]) {
          $scope.current_article = article;
        }
      });
    }
  };

  $scope.$watch(function() {
    return $location.path();
  }, $scope.updateCurrents);
  $scope.$watch(function() {
    return $scope.index;
  }, $scope.updateCurrents, true);
})